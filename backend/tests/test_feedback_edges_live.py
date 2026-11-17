"""Feedback edge cases: auth, validation, stats deltas, privacy of stored docs, orphan docs after delete (live API)."""
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
COLLS = ("ratings", "confirmations_pregnancy", "confirmations_birth")
FAM = {"wife": ["male", "male", "female"], "husband": ["female", "male", "female"], "child_number": 1}
NO_RESULT = {"wife": ["male"], "husband": ["female"]}


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
    created = []
    with as_role(s, API, "member"):
        yield {"s": s, "created": created}
    for i in created:
        s.delete(f"{API}/analyses/{i}")
    for coll in COLLS:
        _db[coll].delete_many({"analysis_id": {"$in": created}})


def _stats(s):
    with as_role(s, API, "admin"):
        return s.get(f"{API}/admin/stats").json()


def test_unauthenticated_401(ctx):
    assert requests.get(f"{API}/admin/stats").status_code == 401
    assert requests.put(f"{API}/analyses/abc/rating", json={"value": "like"}).status_code == 401


def test_invalid_id_and_body(ctx):
    s = ctx["s"]
    assert s.put(f"{API}/analyses/notanid/rating", json={"value": "like"}).status_code in (400, 404)
    r = s.post(f"{API}/analyses/family-pattern", json=FAM)
    aid = r.json()["id"]
    ctx["created"].append(aid)
    assert s.put(f"{API}/analyses/{aid}/confirmations/birth", json={"actual": "boy"}).status_code == 422
    assert s.put(f"{API}/analyses/{aid}/confirmations/birth", json={"actual": "male", "x": 1}).status_code == 422


def test_no_outcome_family_not_confirmable(ctx):
    s = ctx["s"]
    r = s.post(f"{API}/analyses/family-pattern", json=NO_RESULT)
    assert r.status_code in (200, 201), r.text
    aid = r.json()["id"]
    ctx["created"].append(aid)
    fb = s.get(f"{API}/analyses/{aid}/feedback").json()
    assert fb["confirmable"] is False
    assert s.put(f"{API}/analyses/{aid}/confirmations/pregnancy", json={"actual": "male"}).status_code == 400


def _assert_stage_delta(before, after, actual, matched):
    assert after["confirmed"] == before["confirmed"] + 1
    assert after["matches"] == before["matches"] + int(matched)
    assert after["actual"][actual] == before["actual"][actual] + 1


def _assert_no_private_fields(aid):
    for coll in COLLS:
        doc = _db[coll].find_one({"analysis_id": aid})
        assert doc and not {"user_id", "email", "name", "wife", "husband", "inputs", "details"} & set(doc), doc


def test_stats_deltas_consistent(ctx):
    s = ctx["s"]
    before = _stats(s)
    aid = s.post(f"{API}/analyses/family-pattern", json={**FAM, "child_number": 2}).json()["id"]
    ctx["created"].append(aid)
    assert _stats(s)["predictions_total"] == before["predictions_total"] + 1
    s.put(f"{API}/analyses/{aid}/confirmations/pregnancy", json={"actual": "male"})
    s.put(f"{API}/analyses/{aid}/confirmations/birth", json={"actual": "female"})
    s.put(f"{API}/analyses/{aid}/rating", json={"value": "like"})
    after = _stats(s)
    pred = _db.confirmations_pregnancy.find_one({"analysis_id": aid})["predicted"]
    _assert_stage_delta(before["stages"]["pregnancy"], after["stages"]["pregnancy"], "male", pred == "male")
    _assert_stage_delta(before["stages"]["birth"], after["stages"]["birth"], "female", pred == "female")
    assert after["confirmed_total"] == before["confirmed_total"] + 1  # distinct predictions confirmed
    assert after["ratings"]["likes"] == before["ratings"]["likes"] + 1
    s.put(f"{API}/analyses/{aid}/rating", json={"value": "dislike"})
    after2 = _stats(s)["ratings"]
    assert (after2["likes"], after2["dislikes"]) == (before["ratings"]["likes"], before["ratings"]["dislikes"] + 1)
    _assert_no_private_fields(aid)


def test_orphans_after_delete(ctx):
    """Report-only: does deleting the analysis remove its feedback docs?"""
    s = ctx["s"]
    aid = s.post(f"{API}/analyses/family-pattern", json=FAM).json()["id"]
    ctx["created"].append(aid)
    s.put(f"{API}/analyses/{aid}/confirmations/birth", json={"actual": "male"})
    s.put(f"{API}/analyses/{aid}/rating", json={"value": "like"})
    assert s.delete(f"{API}/analyses/{aid}").status_code in (200, 204)
    left = {c: _db[c].count_documents({"analysis_id": aid}) for c in COLLS}
    print("ORPHANS_AFTER_DELETE", left)
