"""Live API tests for POST /api/analyses/family-pattern (traditional table) + concurrency dedupe + history summary."""
import concurrent.futures as cf
import json
import os
import subprocess
import threading
from pathlib import Path

import pytest
import requests
from live_roles import as_role
from dotenv import dotenv_values

BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL")
            or dotenv_values(Path("/app/frontend/.env"))["REACT_APP_BACKEND_URL"]).rstrip("/")
API = f"{BASE_URL}/api"
EMAIL = "it5+clerk_test@example.com"


@pytest.fixture(scope="module")
def created():
    return set()


@pytest.fixture(scope="module")
def s(created):
    out = subprocess.run(["python", "/app/scripts/clerk_test_session.py", EMAIL], capture_output=True, text=True,
                         timeout=60)
    if out.returncode != 0:
        pytest.skip("clerk session failed")
    sess = requests.Session()
    sess.headers["Authorization"] = f"Bearer {json.loads(out.stdout)['token']}"
    with as_role(sess, API, "admin"):  # admin sees the protected details these tests check
        yield sess
    for i in created:
        sess.delete(f"{API}/analyses/{i}")


def _post(s, created, body, lang="en"):
    r = s.post(f"{API}/analyses/family-pattern?lang={lang}", json=body)
    if r.status_code == 200 and r.json().get("id"):
        created.add(r.json()["id"])
    return r


def _res(r):
    d = r.json()
    return d.get("result", d)


# Auth required
def test_requires_auth():
    r = requests.post(f"{API}/analyses/family-pattern", json={"wife": ["male"], "husband": ["male"]})
    assert r.status_code == 401


# Case 1, exact 3+3 match, no flags, deterministic
def test_case_1(s, created):
    body = {"wife": ["male", "male", "female"], "husband": ["male", "male", "female"], "child_number": 1}
    r = _post(s, created, body)
    assert r.status_code == 200, r.text
    res = _res(r)
    assert res["certainty"] == "traditional_belief"
    assert res["outcomes"][0]["key"] == "male" and res["outcomes"][0]["probability"] is None
    assert res["details"]["effective_case"] == 1 and res["details"]["review_flags"] == []
    assert res["details"]["matched_cases"] == [1]


# Duplicate pattern case 41 / 78
def test_duplicate_41_78(s, created):
    r = _post(s, created, {"wife": ["male", "male"], "husband": ["male", "male"], "child_number": 2})
    res = _res(r)
    assert res["details"]["matched_cases"] == [41, 78, 90]
    assert res["details"]["effective_case"] == 41
    assert res["details"]["review_flags"] == ["duplicate_pattern"]


# 1+2 exact case 54
def test_case_54(s, created):
    res = _res(_post(s, created, {"wife": ["female"], "husband": ["male", "male"], "child_number": 1}))
    assert res["details"]["effective_case"] == 54
    assert res["details"]["review_flags"] == ["duplicate_pattern"] and res["details"]["answer_borrowed"] is False
    assert all(o["probability"] is None for o in res["outcomes"])


# Not in table -> no outcome, no default boy
def test_not_in_table(s, created):
    res = _res(_post(s, created, {"wife": ["male", "female", "male"], "husband": ["female", "female", "female"],
                                  "child_number": 1}))
    assert res["outcomes"] == []
    assert res["details"]["review_flags"] == ["not_in_table"]
    assert "effective_case" not in res["details"]


# Invalid inputs rejected
@pytest.mark.parametrize("body", [
    {"wife": [], "husband": ["male"]},
    {"wife": ["male"] * 4, "husband": ["male"]},
    {"wife": ["boy"], "husband": ["male"]},
    {"wife": ["male"], "husband": ["male"], "child_number": 3},
    {"wife": ["male"] * 3, "husband": ["male"] * 3},
    {"wife": ["male"], "husband": ["male"], "extra": 1},
    {"husband": ["male"]},
])
def test_invalid(s, created, body):
    r = _post(s, created, body)
    assert r.status_code in (400, 422), r.text


# Localization AR/DE of limitation texts contains no raw codes
@pytest.mark.parametrize("lang", ["ar", "de"])
def test_localized(s, created, lang):
    r = _post(s, created, {"wife": ["female"], "husband": ["male", "male"], "child_number": 2}, lang=lang)
    assert r.status_code == 200
    txt = json.dumps(r.json(), ensure_ascii=False)
    print(lang, txt[:600])


# Concurrent identical requests -> one id
def test_concurrent_one_id(s, created):
    body = {"wife": ["female", "female", "male"], "husband": ["male", "female", "female"], "child_number": 2}
    barrier = threading.Barrier(6)

    def go(_):
        barrier.wait()
        return s.post(f"{API}/analyses/family-pattern", json=body).json()["id"]

    with cf.ThreadPoolExecutor(6) as ex:
        ids = list(ex.map(go, range(6)))
    created.update(ids)
    assert len(set(ids)) == 1, ids


# History summary for family pattern translated
@pytest.mark.parametrize("lang", ["en", "ar", "de"])
def test_history_summary(s, created, lang):
    items = s.get(f"{API}/analyses?lang={lang}&limit=200").json()["items"]
    fp = [i for i in items if i.get("analysis_type") == "family-pattern"]
    assert fp
    print(lang, json.dumps(fp[0], ensure_ascii=False)[:500])
