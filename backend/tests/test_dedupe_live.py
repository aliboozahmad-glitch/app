"""Live tests for server-side duplicate prevention (DEDUPE_WINDOW_S=10) on POST /api/analyses/{kind}."""
import concurrent.futures as cf
import json
import os
import secrets
import subprocess
import time
from pathlib import Path

import pytest
import requests
from dotenv import dotenv_values

BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL")
            or dotenv_values(Path("/app/frontend/.env"))["REACT_APP_BACKEND_URL"]).rstrip("/")
API = f"{BASE_URL}/api"
USER_A = "genova.tester+clerk_test@example.com"
USER_B = "genova.other+clerk_test@example.com"


def _client(email, created):
    out = subprocess.run(["python", "/app/scripts/clerk_test_session.py", email], capture_output=True, text=True,
                         timeout=60)
    if out.returncode != 0:
        pytest.skip("clerk session failed")
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {json.loads(out.stdout)['token']}"
    return s


@pytest.fixture(scope="module")
def created():
    return {"a": set(), "b": set()}


@pytest.fixture(scope="module")
def a(created):
    s = _client(USER_A, created)
    yield s
    for i in created["a"]:
        s.delete(f"{API}/analyses/{i}")


@pytest.fixture(scope="module")
def b(created):
    s = _client(USER_B, created)
    yield s
    for i in created["b"]:
        s.delete(f"{API}/analyses/{i}")


def _body():
    # unique heights so parallel runs never collide
    return {"mother_cm": 150 + secrets.randbelow(300) / 10, "father_cm": 160 + secrets.randbelow(400) / 10}


def _count(s):
    return len(s.get(f"{API}/analyses?limit=200").json()["items"])


def _post(s, body, bucket):
    r = s.post(f"{API}/analyses/height", json=body)
    assert r.status_code == 200, r.text
    bucket.add(r.json()["id"])
    return r.json()


# Sequential rapid repeats -> one entry
def test_sequential_triple_post_dedupes(a, created):
    body = _body()
    before = _count(a)
    r1, r2, r3 = (_post(a, body, created["a"]) for _ in range(3))
    assert r1["id"] == r2["id"] == r3["id"]
    assert not r1.get("deduplicated")
    assert r2["deduplicated"] is True and r3["deduplicated"] is True
    assert r2["result"] == r1["result"]
    assert _count(a) == before + 1


# Concurrent (parallel) repeats -> race check
def test_concurrent_triple_post_dedupes(a, created):
    body = _body()
    before = _count(a)
    with cf.ThreadPoolExecutor(3) as ex:
        res = list(ex.map(lambda _: _post(a, body, created["a"]), range(3)))
    ids = {r["id"] for r in res}
    print("concurrent ids:", ids)
    assert len(ids) == 1, f"concurrent POSTs created {len(ids)} entries"
    assert _count(a) == before + 1


# Different inputs -> new entry
def test_different_inputs_new_entry(a, created):
    r1 = _post(a, _body(), created["a"])
    r2 = _post(a, _body(), created["a"])
    assert r1["id"] != r2["id"]
    assert not r2.get("deduplicated")


# Same inputs from another user -> separate entry
def test_other_user_separate_entry(a, b, created):
    body = _body()
    ra = _post(a, body, created["a"])
    rb = _post(b, body, created["b"])
    assert ra["id"] != rb["id"]
    assert not rb.get("deduplicated")
    assert b.get(f"{API}/analyses/{ra['id']}").status_code == 404


# Dedup response respects lang
def test_dedup_response_localized(a, created):
    body = _body()
    _post(a, body, created["a"])
    r = a.post(f"{API}/analyses/height?lang=de", json=body).json()
    assert r["deduplicated"] is True
    assert r["result"]["lang"] == "de"


# After window -> intentional recalculation
def test_after_window_new_entry(a, created):
    body = _body()
    r1 = _post(a, body, created["a"])
    time.sleep(11)
    r2 = _post(a, body, created["a"])
    assert r1["id"] != r2["id"]
    assert not r2.get("deduplicated")


# Float vs int equivalence (70 vs 70.0) behaviour - informational
def test_int_vs_float_same(a, created):
    m = 150 + secrets.randbelow(31)
    r1 = _post(a, {"mother_cm": m, "father_cm": 175}, created["a"])
    r2 = _post(a, {"mother_cm": float(m), "father_cm": 175.0}, created["a"])
    assert r1["id"] == r2["id"]
