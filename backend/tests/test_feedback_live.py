"""Voluntary confirmations, ratings and admin statistics (live API)."""
import json
import os
import subprocess
from pathlib import Path

import pytest
import requests
from dotenv import dotenv_values
from live_roles import _db, as_role

BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL")
            or dotenv_values(Path("/app/frontend/.env"))["REACT_APP_BACKEND_URL"]).rstrip("/")
API = f"{BASE_URL}/api"


def _session(email):
    out = subprocess.run(["python", "/app/scripts/clerk_test_session.py", email], capture_output=True, text=True,
                         timeout=60)
    if out.returncode != 0:
        pytest.skip("clerk session failed")
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {json.loads(out.stdout)['token']}"
    return s


@pytest.fixture(scope="module")
def ctx():
    s = _session("genova.fb+clerk_test@example.com")
    other = _session("genova.other+clerk_test@example.com")
    with as_role(s, API, "member"):
        fam = s.post(f"{API}/analyses/family-pattern",
                     json={"wife": ["male", "male", "female"], "husband": ["female", "male", "female"],
                           "child_number": 1}).json()["id"]
        blood_in = {"parent1_abo": "A", "parent1_rh": "+", "parent2_abo": "B", "parent2_rh": "+"}
        blood = s.post(f"{API}/analyses/blood-type", json=blood_in).json()["id"]
        yield {"s": s, "other": other, "fam": fam, "blood": blood}
    for i in (fam, blood):
        s.delete(f"{API}/analyses/{i}")
    for coll in ("ratings", "confirmations_pregnancy", "confirmations_birth"):
        _db[coll].delete_many({"analysis_id": {"$in": [fam, blood]}})


def test_rating_one_per_result_and_changeable(ctx):
    s, fam = ctx["s"], ctx["fam"]
    assert s.put(f"{API}/analyses/{fam}/rating", json={"value": "like"}).status_code == 200
    assert s.put(f"{API}/analyses/{fam}/rating", json={"value": "dislike"}).status_code == 200
    docs = list(_db.ratings.find({"analysis_id": fam}))
    assert len(docs) == 1 and docs[0]["value"] == "dislike" and "user_id" not in docs[0]
    assert s.get(f"{API}/analyses/{fam}/feedback").json()["rating"] == "dislike"
    assert s.put(f"{API}/analyses/{fam}/rating", json={"value": "meh"}).status_code == 422


def test_rating_any_calculator(ctx):
    s, blood = ctx["s"], ctx["blood"]
    assert s.put(f"{API}/analyses/{blood}/rating", json={"value": "like"}).status_code == 200
    fb = s.get(f"{API}/analyses/{blood}/feedback").json()
    assert fb["rating"] == "like" and fb["confirmable"] is False


def test_confirmations_separate_and_correctable(ctx):
    s, fam = ctx["s"], ctx["fam"]
    assert s.put(f"{API}/analyses/{fam}/confirmations/pregnancy", json={"actual": "female"}).status_code == 200
    assert s.put(f"{API}/analyses/{fam}/confirmations/pregnancy", json={"actual": "male"}).status_code == 200
    assert s.put(f"{API}/analyses/{fam}/confirmations/birth", json={"actual": "female"}).status_code == 200
    preg = list(_db.confirmations_pregnancy.find({"analysis_id": fam}))
    birth = list(_db.confirmations_birth.find({"analysis_id": fam}))
    assert len(preg) == 1 and len(birth) == 1
    p, b = preg[0], birth[0]
    assert (p["stage"], p["predicted"], p["actual"], p["match"]) == ("pregnancy", "male", "male", True)
    assert (b["stage"], b["actual"], b["match"]) == ("birth", "female", False)
    assert p["stated_range"] == "70\u201390%" and p["method_group"] == "two_child_table"
    for doc in (p, b):
        assert not {"user_id", "email", "name", "wife", "husband"} & set(doc)
    fb = s.get(f"{API}/analyses/{fam}/feedback").json()
    assert fb["confirmations"]["pregnancy"]["actual"] == "male" and fb["confirmations"]["birth"]["actual"] == "female"


def test_confirmation_rules(ctx):
    s, other = ctx["s"], ctx["other"]
    assert s.put(f"{API}/analyses/{ctx['blood']}/confirmations/birth", json={"actual": "male"}).status_code == 400
    assert s.put(f"{API}/analyses/{ctx['fam']}/confirmations/later", json={"actual": "male"}).status_code == 422
    assert other.put(f"{API}/analyses/{ctx['fam']}/confirmations/birth", json={"actual": "male"}).status_code == 404
    assert other.put(f"{API}/analyses/{ctx['fam']}/rating", json={"value": "like"}).status_code == 404
    assert other.get(f"{API}/analyses/{ctx['fam']}/feedback").status_code == 404


def test_admin_stats_admin_only(ctx):
    s = ctx["s"]
    assert s.get(f"{API}/admin/stats").status_code == 403
    with as_role(s, API, "admin"):
        st = s.get(f"{API}/admin/stats").json()
    assert st["label"] == "voluntary_user_reported_observational"
    preg, birth = st["stages"]["pregnancy"], st["stages"]["birth"]
    assert preg["confirmed"] >= 1 and birth["confirmed"] >= 1
    assert [m["method"] for m in preg["by_method"]] == ["two_child_table", "one_child_table", "other_case_answer"]
    assert any(r["range"] == "70\u201390%" for r in preg["by_range"])
    assert preg["matches"] + preg["mismatches"] == preg["confirmed"]
    assert set(st["ratings"]) >= {"likes", "dislikes", "total", "satisfaction", "by_type"}
