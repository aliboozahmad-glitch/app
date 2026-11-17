import asyncio
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from . import genetics as g
from .auth import IN_ENV, RANK, ROLES, current_member, effective_role, require_role
from .db import db
from .genetics.data_loader import disease_list, load_diseases, load_references
from .i18n import localize_result, t
from .models import (
    AnalysisDoc,
    BloodTypeIn,
    CarrierIn,
    FamilyPatternIn,
    HeightIn,
    Lang,
    MendelianIn,
    PigmentIn,
    RoleIn,
    SexRatioIn,
)
from .protection import DAILY_LIMIT, PROTECTED_KIND, protect_item, protect_view
from .ratelimit import analysis_limiter
from .stats_log import log_prediction
from .traditional import family_pattern_analysis

router = APIRouter(prefix="/api")
DEDUPE_WINDOW_S = 10
# Single-process lock; replace with a unique request-hash index when running several workers.
_save_locks: defaultdict = defaultdict(asyncio.Lock)

CALCULATORS = {
    "mendelian": (MendelianIn, lambda b: g.mendelian_analysis(b.mode, b.parent1, b.parent2)),
    "blood-type": (BloodTypeIn,
                   lambda b: g.blood_type_analysis(b.parent1_abo, b.parent1_rh, b.parent2_abo, b.parent2_rh)),
    "carrier-risk": (CarrierIn, lambda b: g.carrier_analysis(b.disease_id, b.mother_status, b.father_status, b.region)),
    "height": (HeightIn, lambda b: g.height_analysis(b.mother_cm, b.father_cm)),
    "pigmentation": (PigmentIn, lambda b: g.pigmentation_analysis(b.trait, b.mother, b.father)),
    "sex-ratio": (SexRatioIn, lambda b: g.sex_ratio_analysis()),
    "family-pattern": (FamilyPatternIn, lambda b: family_pattern_analysis(b.wife, b.husband, b.child_number)),
}


def _oid(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except (InvalidId, TypeError) as exc:
        raise HTTPException(status_code=404, detail="Not found") from exc


def _view(doc: AnalysisDoc, lang: str, role: str) -> dict:
    view = {"id": doc.id, "analysis_type": doc.analysis_type, "created_at": doc.created_at, "request": doc.request,
            "result": localize_result(doc.result, lang)}
    return protect_view(view, role)


def _daily_key(member: dict, kind: str) -> dict | None:
    """Saved calculations per UTC day; deleting history does not reset it. Admin is not limited."""
    if kind != PROTECTED_KIND or member["role"] == "admin":
        return None
    return {"user_id": member["user_id"], "kind": kind, "day": datetime.now(UTC).date().isoformat()}


async def _check_daily_limit(key: dict | None, lang: str) -> None:
    used = await db.usage_daily.find_one(key) if key else None
    if used and used["count"] >= DAILY_LIMIT:
        raise HTTPException(status_code=429, detail=t("daily_limit_reached", lang))


async def _recent_duplicate(user_id: str, kind: str, request: dict) -> AnalysisDoc | None:
    """Same user, same calculator, same inputs within the window = one intentional calculation."""
    cutoff = (datetime.now(UTC) - timedelta(seconds=DEDUPE_WINDOW_S)).isoformat()
    raw = await db.analyses.find_one(
        {"user_id": user_id, "analysis_type": kind, "request": request, "created_at": {"$gte": cutoff}},
        sort=[("created_at", -1)])
    return AnalysisDoc.from_mongo(raw) if raw else None


@router.get("/health")
async def health():
    return {"status": "ok", "engine_version": g.ENGINE_VERSION}


@router.get("/catalog")
async def catalog(lang: Lang = "en"):
    regions = load_diseases().get("_regions") or ["gulf", "middle_east_north_africa", "europe", "sub_saharan_africa",
                                                  "south_asia", "east_asia", "americas", "global"]
    diseases = [{"id": d["id"], "name": d["names"][lang], "gene": d["gene"], "inheritance": d["inheritance"],
                 "inheritance_label": t(d["inheritance"], lang), "is_trait": d["is_trait"],
                 "female_variable_expression": d.get("female_variable_expression", False),
                 "references": d["references"],
                 "regional": [{"region": r["region"], "region_label": t(r["region"], lang), "status": r["status"],
                               "source": r["source"], "candidate": r.get("candidate")} for r in d.get("regional", [])]}
                for d in disease_list()]
    return {"engine_version": g.ENGINE_VERSION, "data_version": load_diseases()["_version"],
            "modes": [{"id": m, "label": t(m, lang)} for m in g.MODES],
            "regions": [{"id": r, "label": t(r, lang)} for r in regions], "diseases": diseases}


@router.get("/references")
async def references():
    return {"references": [r for r in load_references().values() if not r.get("internal")]}


@router.get("/me")
async def me(member: dict = Depends(current_member)):
    return {"user_id": member["user_id"], "role": member["role"], "email": member.get("email")}


@router.post("/analyses/{kind}")
async def run_analysis(kind: str, body: dict, lang: Lang = "en", member: dict = Depends(current_member)):
    if kind not in CALCULATORS:
        raise HTTPException(status_code=404, detail="Unknown analysis")
    schema, fn = CALCULATORS[kind]
    try:
        payload = schema.model_validate(body)
    except ValidationError as exc:
        raise RequestValidationError([{**e, "loc": ("body", *e["loc"])} for e in exc.errors()]) from exc
    analysis_limiter.check(member["user_id"])
    request = payload.model_dump()
    async with _save_locks[(member["user_id"], kind)]:  # check + insert are atomic per user and calculator
        duplicate = await _recent_duplicate(member["user_id"], kind, request)
        if duplicate:
            return {**_view(duplicate, lang, member["role"]), "deduplicated": True}
        daily = _daily_key(member, kind)
        await _check_daily_limit(daily, lang)
        doc = AnalysisDoc(user_id=member["user_id"], analysis_type=kind, request=request, result=fn(payload))
        res = await db.analyses.insert_one(doc.to_mongo())
        if daily:
            await db.usage_daily.update_one(daily, {"$inc": {"count": 1}}, upsert=True)
        doc.id = str(res.inserted_id)
        await log_prediction(doc.id, kind, doc.result, doc.created_at)
        return _view(doc, lang, member["role"])


@router.get("/analyses")
async def list_analyses(lang: Lang = "en", limit: int = Query(50, ge=1, le=200),
                        member: dict = Depends(current_member)):
    cursor = db.analyses.find({"user_id": member["user_id"]}).sort("created_at", -1).limit(limit)
    items = []
    async for raw in cursor:
        d = AnalysisDoc.from_mongo(raw)
        loc = localize_result(d.result, lang)
        item = {"id": d.id, "analysis_type": d.analysis_type, "created_at": d.created_at, "request": d.request,
                "certainty": d.result["certainty"], "certainty_label": loc["certainty_label"],
                "method_label": loc["method_label"], "disease_name": loc["details"].get("disease_name")}
        items.append(protect_item(item, member["role"], lang))
    return {"items": items}


@router.get("/analyses/{analysis_id}")
async def get_analysis(analysis_id: str, lang: Lang = "en", member: dict = Depends(current_member)):
    raw = await db.analyses.find_one({"_id": _oid(analysis_id), "user_id": member["user_id"]})
    if not raw:
        raise HTTPException(status_code=404, detail="Not found")
    return _view(AnalysisDoc.from_mongo(raw), lang, member["role"])


@router.delete("/analyses/{analysis_id}")
async def delete_analysis(analysis_id: str, member: dict = Depends(current_member)):
    res = await db.analyses.delete_one({"_id": _oid(analysis_id), "user_id": member["user_id"]})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": True}


@router.get("/users")
async def list_users(admin: dict = Depends(require_role("admin"))):
    people = await db.users.find(IN_ENV, {"_id": 0}).to_list(1000)
    return {"roles": [r for r in ROLES if RANK[r] <= RANK[admin["role"]]],
            "users": [{**p, "role": effective_role(p.get("role"))} for p in people]}


@router.patch("/users/{user_id}/role")
async def set_role(user_id: str, body: RoleIn, admin: dict = Depends(require_role("admin"))):
    if body.role not in ROLES or RANK[body.role] > RANK[admin["role"]]:
        raise HTTPException(status_code=403, detail="Not allowed")
    target = await db.users.find_one({"user_id": user_id, **IN_ENV}, {"_id": 0})
    if target is None:
        raise HTTPException(status_code=404, detail="Not found")
    if (effective_role(target.get("role")) == "admin" and body.role != "admin"
            and await db.users.count_documents({"role": "admin", **IN_ENV}) <= 1):
        raise HTTPException(status_code=409, detail="Keep at least one admin")
    await db.users.update_one({"user_id": user_id}, {"$set": {"role": body.role}})
    return {"user_id": user_id, "role": body.role}
