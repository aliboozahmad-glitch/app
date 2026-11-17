"""Voluntary real-world confirmations, Like/Dislike ratings and admin-only observational statistics.

No names, emails or user ids are stored with confirmations or ratings; ownership is checked at write time.
Pregnancy and birth confirmations live in separate collections. Ratings are kept apart from accuracy data.
"""
from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException

from .api import _oid
from .auth import current_member, require_role
from .db import db
from .limits import limit_stats
from .models import Gender, Strict
from .protection import PROTECTED_KIND
from .stats_log import snapshot

router = APIRouter(prefix="/api")
Stage = Literal["pregnancy", "birth"]
STAGE_COLLECTIONS = {"pregnancy": "confirmations_pregnancy", "birth": "confirmations_birth"}
METHODS = ("two_child_table", "one_child_table", "other_case_answer")
DISTINCT_CONFIRMED = [{"$project": {"analysis_id": 1}},
                      {"$unionWith": {"coll": "confirmations_birth", "pipeline": [{"$project": {"analysis_id": 1}}]}},
                      {"$group": {"_id": "$analysis_id"}}, {"$count": "n"}]


class RatingIn(Strict):
    value: Literal["like", "dislike"]


class ConfirmationIn(Strict):
    actual: Gender


async def _owned(analysis_id: str, member: dict) -> dict:
    raw = await db.analyses.find_one({"_id": _oid(analysis_id), "user_id": member["user_id"]})
    if not raw:
        raise HTTPException(status_code=404, detail="Not found")
    return raw


def _snapshot(raw: dict) -> dict:
    if raw["analysis_type"] != PROTECTED_KIND or not raw["result"].get("outcomes"):
        raise HTTPException(status_code=400, detail="Nothing to confirm for this result")
    return snapshot(raw["result"])


def _now() -> str:
    return datetime.now(UTC).isoformat()


@router.get("/analyses/{analysis_id}/feedback")
async def get_feedback(analysis_id: str, member: dict = Depends(current_member)):
    raw = await _owned(analysis_id, member)
    rating = await db.ratings.find_one({"analysis_id": analysis_id}, {"_id": 0, "value": 1})
    confirmations = {}
    for stage, coll in STAGE_COLLECTIONS.items():
        doc = await db[coll].find_one({"analysis_id": analysis_id}, {"_id": 0, "actual": 1, "updated_at": 1})
        confirmations[stage] = doc
    confirmable = raw["analysis_type"] == PROTECTED_KIND and bool(raw["result"].get("outcomes"))
    return {"rating": rating["value"] if rating else None, "confirmable": confirmable,
            "confirmations": confirmations}


@router.put("/analyses/{analysis_id}/rating")
async def set_rating(analysis_id: str, body: RatingIn, member: dict = Depends(current_member)):
    raw = await _owned(analysis_id, member)
    now = _now()
    await db.ratings.update_one(
        {"analysis_id": analysis_id},
        {"$set": {"value": body.value, "analysis_type": raw["analysis_type"], "updated_at": now},
         "$setOnInsert": {"created_at": now}}, upsert=True)
    return {"rating": body.value}


@router.put("/analyses/{analysis_id}/confirmations/{stage}")
async def set_confirmation(analysis_id: str, stage: Stage, body: ConfirmationIn,
                           member: dict = Depends(current_member)):
    snap = _snapshot(await _owned(analysis_id, member))
    now = _now()
    await db[STAGE_COLLECTIONS[stage]].update_one(
        {"analysis_id": analysis_id},
        {"$set": {**snap, "stage": stage, "actual": body.actual, "match": snap["predicted"] == body.actual,
                  "updated_at": now}, "$setOnInsert": {"created_at": now}}, upsert=True)
    return {"stage": stage, "actual": body.actual, "updated_at": now}


def _rate(part: int, total: int) -> float | None:
    return round(100 * part / total, 1) if total else None


def _block(rows: list) -> dict:
    total = sum(r["n"] for r in rows)
    matches = sum(r["n"] for r in rows if r["_id"]["match"])
    return {"confirmed": total, "matches": matches, "mismatches": total - matches,
            "match_rate": _rate(matches, total)}


def _grouped(rows: list, field: str, keys) -> list:
    return [{field: k, **_block([r for r in rows if r["_id"][field] == k])} for k in keys]


async def _stage_stats(coll: str) -> dict:
    rows = await db[coll].aggregate([{"$group": {
        "_id": {"match": "$match", "actual": "$actual", "range": "$stated_range", "method": "$method_group"},
        "n": {"$sum": 1}}}]).to_list(None)
    ranges = sorted({r["_id"]["range"] for r in rows}, key=lambda x: (x is None, x or ""))
    actual = {g: sum(r["n"] for r in rows if r["_id"]["actual"] == g) for g in ("male", "female")}
    return {**_block(rows), "actual": actual, "by_range": _grouped(rows, "range", ranges),
            "by_method": _grouped(rows, "method", METHODS)}


async def _rating_stats() -> dict:
    rows = await db.ratings.aggregate([{"$group": {"_id": {"type": "$analysis_type", "value": "$value"},
                                                   "n": {"$sum": 1}}}]).to_list(None)

    def summary(sel: list) -> dict:
        likes = sum(r["n"] for r in sel if r["_id"]["value"] == "like")
        dislikes = sum(r["n"] for r in sel if r["_id"]["value"] == "dislike")
        return {"likes": likes, "dislikes": dislikes, "total": likes + dislikes,
                "satisfaction": _rate(likes, likes + dislikes)}

    types = sorted({r["_id"]["type"] for r in rows})
    return {**summary(rows),
            "by_type": [{"analysis_type": k, **summary([r for r in rows if r["_id"]["type"] == k])} for k in types]}


@router.get("/admin/stats")
async def admin_stats(_: dict = Depends(require_role("admin"))):
    predictions = await db.prediction_log.count_documents({})
    distinct = await db.confirmations_pregnancy.aggregate(DISTINCT_CONFIRMED).to_list(None)
    stages = {stage: await _stage_stats(coll) for stage, coll in STAGE_COLLECTIONS.items()}
    return {"label": "voluntary_user_reported_observational", "predictions_total": predictions,
            "confirmed_total": distinct[0]["n"] if distinct else 0, "stages": stages,
            "ratings": await _rating_stats(), "limits": await limit_stats()}
