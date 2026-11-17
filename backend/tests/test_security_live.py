"""Live security checks: network-wide daily limit, admin limit counts, tampered tokens, headers, no route listing."""
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest
import requests
from dotenv import dotenv_values
from live_roles import _db, as_role

BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL")
            or dotenv_values(Path("/app/frontend/.env"))["REACT_APP_BACKEND_URL"]).rstrip("/")
API = f"{BASE_URL}/api"
BODY = {"wife": ["female"], "husband": ["male", "female", "male"]}


def _session(email):
    out = subprocess.run(["python", "/app/scripts/clerk_test_session.py", email], capture_output=True, text=True,
                         timeout=60)
    if out.returncode != 0:
        pytest.skip("clerk session failed")
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {json.loads(out.stdout)['token']}"
    return s


@pytest.fixture(scope="module")
def member():
    s = _session("genova.sec+clerk_test@example.com")
    with as_role(s, API, "member"):
        yield s
    for item in s.get(f"{API}/analyses").json()["items"]:
        s.delete(f"{API}/analyses/{item['id']}")


def _network_doc(s):
    """Find this test machine's network counter by the one that a fresh calculation increments."""
    day = datetime.now(UTC).date().isoformat()
    before = {d["network"]: d.get("count", 0) for d in _db.usage_network_daily.find({"day": day})}
    assert s.post(f"{API}/analyses/family-pattern", json=BODY).status_code == 200
    after = {d["network"]: d.get("count", 0) for d in _db.usage_network_daily.find({"day": day})}
    changed = [n for n, c in after.items() if c == before.get(n, 0) + 1]
    assert len(changed) == 1, changed
    return {"network": changed[0], "kind": "family-pattern", "day": day}


def test_network_limit_blocks_all_accounts_on_connection(member):
    key = _network_doc(member)
    original = _db.usage_network_daily.find_one(key)
    try:
        _db.usage_network_daily.update_one(key, {"$set": {"count": 60}})
        r = member.post(f"{API}/analyses/family-pattern?lang=de", json={**BODY, "wife": ["male"]})
        assert r.status_code == 429 and "Internetverbindung" in r.json()["detail"]
        spoof = member.post(f"{API}/analyses/family-pattern", json={**BODY, "wife": ["male", "male"]},
                            headers={"X-Forwarded-For": "203.0.113.9"})
        assert spoof.status_code == 429  # a forged forwarding header does not bypass the limit
        other = member.post(f"{API}/analyses/blood-type",
                            json={"parent1_abo": "A", "parent1_rh": "+", "parent2_abo": "O", "parent2_rh": "+"})
        assert other.status_code == 200  # other calculators are not limited
        assert _db.usage_network_daily.find_one(key)["blocked"] >= original.get("blocked", 0) + 2
        with as_role(member, API, "admin", reset=False):
            assert member.post(f"{API}/analyses/family-pattern", json={**BODY, "wife": ["male"]}).status_code == 200
            limits = member.get(f"{API}/admin/stats").json()["limits"]
        assert limits["network_limit"] == 60 and limits["account_limit"] == 20
        assert limits["networks"]["blocked_attempts"] >= 2 and limits["networks"]["limit_hits"] >= 1
    finally:
        _db.usage_network_daily.update_one(key, {"$set": {"count": original["count"],
                                                          "blocked": original.get("blocked", 0)}})


def test_tampered_and_missing_tokens_rejected(member):
    token = member.headers["Authorization"].split()[1]
    bad = token[:-4] + ("AAAA" if not token.endswith("AAAA") else "BBBB")
    assert requests.get(f"{API}/me", headers={"Authorization": f"Bearer {bad}"}, timeout=30).status_code == 401
    assert requests.get(f"{API}/me", timeout=30).status_code == 401
    assert requests.get(f"{API}/admin/stats", timeout=30).status_code == 401


def test_security_headers_and_no_route_listing():
    r = requests.get(f"{API}/health", timeout=30)
    assert r.headers["X-Frame-Options"] == "DENY"
    assert "max-age=" in r.headers["Strict-Transport-Security"]
    assert r.headers["Content-Security-Policy"].startswith("default-src 'none'")
    for path in ("/api/openapi.json", "/api/docs", "/api/redoc"):
        assert requests.get(f"{BASE_URL}{path}", timeout=30).status_code == 404
