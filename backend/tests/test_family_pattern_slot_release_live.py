# ruff: noqa: F811  (pytest fixture `ctx` is imported from the atomic suite)
"""Iteration 15: 400/422 never consume account or connection slots; repeated near-limit + cold-start races."""
import time

import pytest
from test_family_pattern_network_atomic_live import ACC_MSG, API, DAY, NET_MSG, _db, _fire, _net, _post, _set_net, ctx  # noqa

BAD_33 = {"wife": ["male", "male", "female"], "husband": ["female", "male", "female"]}


def _acc(s):
    return (_db.usage_daily.find_one({"user_id": s.uid, "kind": "family-pattern", "day": DAY}) or {})


# 400 calc error consumes neither account nor connection count, and is not mistaken for a limit block
def test_calc_error_no_account_or_net_slot(ctx):
    s = ctx["sessions"][0]
    _db.usage_daily.delete_many({"user_id": s.uid, "day": DAY})
    _set_net(ctx, 30, 0)
    for _ in range(3):
        r = _post(ctx, s, BAD_33)
        assert r.status_code == 400, r.text
        assert "child_number" in r.text
    assert _net(ctx)["count"] == 30
    assert _acc(s).get("count", 0) == 0


# 422 validation errors consume nothing
def test_validation_error_no_slot(ctx):
    s = ctx["sessions"][1]
    _db.usage_daily.delete_many({"user_id": s.uid, "day": DAY})
    _set_net(ctx, 30, 0)
    for body in [{"wife": ["robot"], "husband": ["male"]}, {"wife": []}, {}]:
        r = s.post(f"{API}/analyses/family-pattern", json=body)
        assert r.status_code == 422, r.text
    assert _net(ctx)["count"] == 30
    assert _acc(s).get("count", 0) == 0


# At a full connection (60) a calc error returns 400 (not 429) and does not touch blocked/count
def test_calc_error_at_full_net(ctx):
    s = ctx["sessions"][2]
    _db.usage_daily.delete_many({"user_id": s.uid, "day": DAY})
    _set_net(ctx, 60, 0)
    r = _post(ctx, s, BAD_33)
    assert r.status_code == 400, r.text
    doc = _net(ctx)
    assert doc["count"] == 60 and doc.get("blocked", 0) == 0
    # a valid request is then blocked by the connection limit
    r = _post(ctx, s)
    assert r.status_code == 429 and NET_MSG in r.json()["detail"]
    assert _net(ctx)["count"] == 60 and _net(ctx)["blocked"] == 1
    assert _acc(s).get("count", 0) == 0


# Calc error at account limit returns 400 and leaves account blocked counter at 0
def test_calc_error_at_account_limit(ctx):
    s = ctx["sessions"][3]
    key = {"user_id": s.uid, "kind": "family-pattern", "day": DAY}
    _db.usage_daily.update_one(key, {"$set": {"count": 20, "blocked": 0}}, upsert=True)
    _set_net(ctx, 5, 0)
    r = _post(ctx, s, BAD_33)
    assert r.status_code == 400, r.text
    assert _acc(s)["count"] == 20 and _acc(s).get("blocked", 0) == 0
    assert _net(ctx)["count"] == 5
    _db.usage_daily.delete_many(key)


# Repeated near-limit bursts (mixed with calc errors) never exceed 60
@pytest.mark.parametrize("preset", [55, 58])
def test_mixed_burst_near_limit(ctx, preset):
    time.sleep(20)  # respect 30/min/user
    for s in ctx["sessions"]:
        _db.usage_daily.delete_many({"user_id": s.uid, "day": DAY})
    _set_net(ctx, preset, 0)
    rs = _fire(ctx, 3)
    errs = [_post(ctx, s, BAD_33) for s in ctx["sessions"]]
    ok = [r for r in rs if r.status_code == 200]
    doc = _net(ctx)
    print(preset, [r.status_code for r in rs], [e.status_code for e in errs], doc.get("count"), doc.get("blocked"))
    assert all(e.status_code == 400 for e in errs)
    assert doc["count"] == 60
    assert len(ok) == 60 - preset
    assert doc["blocked"] == len(rs) - len(ok)
    assert sum(_acc(s).get("count", 0) for s in ctx["sessions"]) == len(ok)


# Cold start repeated 3 times with 3 concurrent per account (12 at once) - never wrongly blocked
def test_cold_start_repeated(ctx):
    for i in range(3):
        time.sleep(20)
        for s in ctx["sessions"]:
            _db.usage_daily.delete_many({"user_id": s.uid, "day": DAY})
        _db.usage_network_daily.delete_many(ctx["net"])
        rs = _fire(ctx, 3)
        codes = [r.status_code for r in rs]
        print("cold", i, codes, _net(ctx).get("count"))
        assert codes.count(200) == len(rs), [r.text[:120] for r in rs if r.status_code != 200]
        assert _net(ctx)["count"] == len(rs)
