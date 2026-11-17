"""Iteration 14: atomic per-connection family-pattern slot reservation (60/day), concurrency + slot accounting."""
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from itertools import product
from pathlib import Path

import pytest
import requests
from dotenv import dotenv_values
from live_roles import _db

BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL")
            or dotenv_values(Path("/app/frontend/.env"))["REACT_APP_BACKEND_URL"]).rstrip("/")
API = f"{BASE_URL}/api"
DAY = datetime.now(UTC).date().isoformat()
EMAILS = ["genova.tester+clerk_test@example.com", "genova.other+clerk_test@example.com",
          "genova.fb+clerk_test@example.com", "genova.sec+clerk_test@example.com"]
NET_MSG = "internet connection"
ACC_MSG = "limit of 20"
G = ["male", "female"]
# unique valid bodies (no 3+3 so child_number is never required)
BODIES = [{"wife": list(w), "husband": list(h)}
          for n, m in [(1, 1), (1, 2), (2, 1), (2, 2), (1, 3), (3, 1)]
          for w in product(G, repeat=n) for h in product(G, repeat=m)]


def _session(email):
    out = subprocess.run(["python", "/app/scripts/clerk_test_session.py", email], capture_output=True, text=True,
                         timeout=60)
    if out.returncode != 0:
        pytest.skip(f"clerk session failed for {email}")
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {json.loads(out.stdout)['token']}"
    s.uid = s.get(f"{API}/me").json()["user_id"]
    return s


@pytest.fixture(scope="module")
def ctx():
    sessions = [_session(e) for e in EMAILS]
    roles = {s.uid: _db.users.find_one({"user_id": s.uid})["role"] for s in sessions}
    for s in sessions:
        _db.users.update_one({"user_id": s.uid}, {"$set": {"role": "member"}})
    created = []
    state = {"sessions": sessions, "created": created, "net": None, "body_i": 0}
    _reset(sessions)
    # discover this machine's connection doc with one request
    r = _post(state, sessions[0])
    assert r.status_code == 200, r.text
    docs = list(_db.usage_network_daily.find({"day": DAY, "kind": "family-pattern"}))
    assert len(docs) == 1, docs
    state["net"] = {"network": docs[0]["network"], "kind": "family-pattern", "day": DAY}
    yield state
    for s in sessions:
        for i in [i for (sid, i) in created if sid == s.uid]:
            s.delete(f"{API}/analyses/{i}")
        _db.users.update_one({"user_id": s.uid}, {"$set": {"role": roles[s.uid]}})
    _reset(sessions)


def _reset(sessions):
    for s in sessions:
        _db.usage_daily.delete_many({"user_id": s.uid, "day": DAY})
    _db.usage_network_daily.delete_many({"day": DAY})


def _next_body(state):
    b = BODIES[state["body_i"] % len(BODIES)]
    state["body_i"] += 1
    return b


def _post(state, s, body=None, lang="en"):
    body = body or _next_body(state)
    r = s.post(f"{API}/analyses/family-pattern?lang={lang}", json=body)
    if r.status_code == 200 and not r.json().get("deduplicated"):
        state["created"].append((s.uid, r.json()["id"]))
    return r


def _net(state):
    return _db.usage_network_daily.find_one(state["net"]) or {}


def _set_net(state, count, blocked=0):
    _db.usage_network_daily.update_one(state["net"], {"$set": {"count": count, "blocked": blocked}}, upsert=True)


def _fire(state, per_account):
    jobs = [(s, _next_body(state)) for s in state["sessions"] for _ in range(per_account)]
    with ThreadPoolExecutor(len(jobs)) as ex:
        return list(ex.map(lambda j: _post(state, j[0], j[1]), jobs))


# Concurrent requests near the limit never push count above 60; extras get 429 + blocked counted
@pytest.mark.parametrize("preset", [57, 59])
def test_concurrent_near_limit(ctx, preset):
    for s in ctx["sessions"]:
        _db.usage_daily.delete_many({"user_id": s.uid, "day": DAY})
    _set_net(ctx, preset, 0)
    rs = _fire(ctx, 3)
    ok = [r for r in rs if r.status_code == 200]
    blocked = [r for r in rs if r.status_code == 429]
    other = [(r.status_code, r.text[:120]) for r in rs if r.status_code not in (200, 429)]
    doc = _net(ctx)
    print(preset, "ok", len(ok), "429", len(blocked), "other", other, "doc", doc.get("count"), doc.get("blocked"))
    assert not other
    assert doc["count"] == 60
    assert len(ok) == 60 - preset
    assert all(NET_MSG in r.json()["detail"] for r in blocked)
    assert doc["blocked"] == len(blocked)
    acc = sum((_db.usage_daily.find_one({"user_id": s.uid, "kind": "family-pattern", "day": DAY}) or {}).get("count", 0)
              for s in ctx["sessions"])
    assert acc == len(ok), f"account counters {acc} vs saved {len(ok)}"


# Cold start: no connection doc yet, concurrent first requests must not be wrongly blocked
def test_concurrent_cold_start(ctx):
    for s in ctx["sessions"]:
        _db.usage_daily.delete_many({"user_id": s.uid, "day": DAY})
    _db.usage_network_daily.delete_many(ctx["net"])
    rs = _fire(ctx, 2)
    codes = [r.status_code for r in rs]
    doc = _net(ctx)
    print("cold codes", codes, "doc", doc.get("count"), doc.get("blocked"))
    assert codes.count(200) == len(rs), [r.text[:120] for r in rs if r.status_code != 200]
    assert doc["count"] == len(rs)


# Normal flow: +1 per saved calc; dedupe, 422, 400 and admin do not consume a slot
def test_slot_accounting(ctx):
    s = ctx["sessions"][1]
    _db.usage_daily.delete_many({"user_id": s.uid, "day": DAY})
    _set_net(ctx, 10, 0)
    body = _next_body(ctx)
    a = _post(ctx, s, body)
    assert a.status_code == 200 and _net(ctx)["count"] == 11
    b = _post(ctx, s, body)
    assert b.json().get("deduplicated") is True and _net(ctx)["count"] == 11, "dedupe consumed slot"
    r = s.post(f"{API}/analyses/family-pattern", json={"wife": ["robot"], "husband": ["male"]})
    assert r.status_code == 422 and _net(ctx)["count"] == 11, "422 consumed slot"
    _db.users.update_one({"user_id": s.uid}, {"$set": {"role": "admin"}})
    try:
        r = _post(ctx, s)
        assert r.status_code == 200 and _net(ctx)["count"] == 11, "admin consumed slot"
    finally:
        _db.users.update_one({"user_id": s.uid}, {"$set": {"role": "member"}})
    acc = _db.usage_daily.find_one({"user_id": s.uid, "kind": "family-pattern", "day": DAY})["count"]
    assert acc == 1


# Calculation error (3+3 without child_number, 400) should not consume a connection slot
def test_calc_error_no_slot(ctx):
    s = ctx["sessions"][2]
    _set_net(ctx, 10, 0)
    r = _post(ctx, s, {"wife": ["male", "male", "female"], "husband": ["female", "male", "female"]})
    print("3+3", r.status_code, r.text[:150], "net", _net(ctx).get("count"))
    assert r.status_code == 400
    assert _net(ctx)["count"] == 10, f"400 error consumed a connection slot: {_net(ctx)['count']}"


# Account limit enforced first; blocked counted in usage_daily.blocked; connection untouched
def test_account_limit_first(ctx):
    s = ctx["sessions"][3]
    key = {"user_id": s.uid, "kind": "family-pattern", "day": DAY}
    _db.usage_daily.update_one(key, {"$set": {"count": 20, "blocked": 0}}, upsert=True)
    _set_net(ctx, 60, 0)
    for _ in range(2):
        r = _post(ctx, s)
        assert r.status_code == 429 and ACC_MSG in r.json()["detail"], r.text
    assert _db.usage_daily.find_one(key)["blocked"] == 2
    doc = _net(ctx)
    assert doc["count"] == 60 and doc.get("blocked", 0) == 0


# Admin stats limits section consistent with stored counters
def test_admin_stats(ctx):
    s = ctx["sessions"][0]
    _db.users.update_one({"user_id": s.uid}, {"$set": {"role": "admin"}})
    try:
        _set_net(ctx, 60, 4)
        lim = s.get(f"{API}/admin/stats").json()["limits"]
    finally:
        _db.users.update_one({"user_id": s.uid}, {"$set": {"role": "member"}})
    print(lim)
    assert lim["account_limit"] == 20 and lim["network_limit"] == 60 and lim["days"] == 30
    since_docs = list(_db.usage_network_daily.find({"blocked": {"$gt": 0}}))
    exp = sum(d["blocked"] for d in since_docs if d["day"] >= min(d["day"] for d in since_docs))
    assert lim["networks"]["blocked_attempts"] >= 4 and lim["networks"]["limit_hits"] >= 1
    assert lim["accounts"]["blocked_attempts"] >= 2  # from test_account_limit_first
    print("expected network blocked (all-time)", exp)
