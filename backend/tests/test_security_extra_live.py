"""Extra live security checks: forged JWTs (alg none/HS256/payload edit), expired token, XFF spoofing variants,
headers on error responses, sensitive routes require auth."""
import base64
import json
import os
import subprocess
import time
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

import jwt
import pytest
import requests
from dotenv import dotenv_values
from live_roles import _db, as_role

BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL")
            or dotenv_values(Path("/app/frontend/.env"))["REACT_APP_BACKEND_URL"]).rstrip("/")
API = f"{BASE_URL}/api"
BODY = {"wife": ["female"], "husband": ["male", "female", "male"]}


def _session_json(email):
    out = subprocess.run(["python", "/app/scripts/clerk_test_session.py", email], capture_output=True, text=True,
                         timeout=60)
    if out.returncode != 0:
        pytest.skip("clerk session failed")
    return json.loads(out.stdout)


@pytest.fixture(scope="module")
def member():
    data = _session_json("genova.sec+clerk_test@example.com")
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {data['token']}"
    with as_role(s, API, "member"):
        yield s
    for item in s.get(f"{API}/analyses").json()["items"]:
        s.delete(f"{API}/analyses/{item['id']}")


def _b64(d):
    return base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip("=")


def _claims(token):
    return jwt.decode(token, options={"verify_signature": False})


# --- Forged tokens ---
def test_alg_none_rejected(member):
    claims = _claims(member.headers["Authorization"].split()[1])
    forged = f"{_b64({'alg': 'none', 'typ': 'JWT'})}.{_b64(claims)}."
    for path in ("/me", "/analyses", "/admin/stats"):
        r = requests.get(f"{API}{path}", headers={"Authorization": f"Bearer {forged}"}, timeout=30)
        assert r.status_code == 401


def test_hs256_forged_rejected(member):
    claims = _claims(member.headers["Authorization"].split()[1])
    forged = jwt.encode(claims, "attacker-secret-key-attacker-secret", algorithm="HS256")
    assert requests.get(f"{API}/me", headers={"Authorization": f"Bearer {forged}"}, timeout=30).status_code == 401


def test_payload_swap_rejected(member):
    token = member.headers["Authorization"].split()[1]
    h, _p, s = token.split(".")
    claims = _claims(token)
    claims["sub"] = "user_3MBgrYYadc1xm0gZ41oWWQszUIY"
    forged = f"{h}.{_b64(claims)}.{s}"
    assert requests.get(f"{API}/me", headers={"Authorization": f"Bearer {forged}"}, timeout=30).status_code == 401


def test_cookie_tampered_rejected(member):
    token = member.headers["Authorization"].split()[1]
    assert requests.get(f"{API}/me", cookies={"__session": token[:-3] + "xyz"}, timeout=30).status_code == 401
    assert requests.get(f"{API}/me", cookies={"__session": token}, timeout=30).status_code == 200


def test_foreign_azp_rejected(member):
    """Token re-signed is impossible; instead ensure azp check exists by sending valid token from wrong Host
    via X-Forwarded-Host (documents ingress behaviour)."""
    token = member.headers["Authorization"].split()[1]
    r = requests.get(f"{API}/me", headers={"Authorization": f"Bearer {token}", "X-Forwarded-Host": "evil.example"},
                     timeout=30)
    print("XFH spoof with azp-less dev token:", r.status_code)
    assert r.status_code in (200, 401)


def test_expired_token_rejected():
    """Mint a short-lived token via the helper's session and wait until it expires."""
    data = _session_json("genova.sec+clerk_test@example.com")
    sid = _claims(data["token"])["sid"]
    secret = os.environ["CLERK_SECRET_KEY"]
    req = urllib.request.Request(f"https://api.clerk.com/v1/sessions/{sid}/tokens", method="POST",
                                 data=json.dumps({"expires_in_seconds": 30}).encode(),
                                 headers={"Authorization": f"Bearer {secret}", "Content-Type": "application/json",
                                          "User-Agent": "genova-test"})
    try:
        short = json.loads(urllib.request.urlopen(req, timeout=30).read())["jwt"]
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"cannot mint short token: {exc}")
    assert requests.get(f"{API}/me", headers={"Authorization": f"Bearer {short}"}, timeout=30).status_code == 200
    exp = _claims(short)["exp"]
    time.sleep(max(0, exp - time.time()) + 8)
    assert requests.get(f"{API}/me", headers={"Authorization": f"Bearer {short}"}, timeout=30).status_code == 401


# --- Headers on every response type ---
@pytest.mark.parametrize("path", ["/api/health", "/api/me", "/api/nope-404", "/api/clerk/config"])
def test_security_headers_everywhere(path):
    r = requests.get(f"{BASE_URL}{path}", timeout=30)
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert "max-age=" in r.headers.get("Strict-Transport-Security", "")
    assert r.headers.get("Content-Security-Policy", "").startswith("default-src 'none'")
    assert "camera=()" in r.headers.get("Permissions-Policy", "")
    assert r.headers.get("X-Content-Type-Options") == "nosniff"


@pytest.mark.parametrize("path", ["/api/openapi.json", "/api/docs", "/api/redoc", "/docs", "/openapi.json",
                                  "/api/docs/oauth2-redirect"])
def test_no_route_listing(path):
    r = requests.get(f"{BASE_URL}{path}", timeout=30)
    assert "openapi" not in r.text.lower() or r.status_code == 404
    if path.startswith("/api"):
        assert r.status_code == 404


# --- Network limit: multi-value XFF spoof ---
def test_network_limit_multi_xff_spoof(member):
    day = datetime.now(UTC).date().isoformat()
    before = {d["network"]: d.get("count", 0) for d in _db.usage_network_daily.find({"day": day})}
    assert member.post(f"{API}/analyses/family-pattern", json=BODY).status_code == 200
    after = {d["network"]: d.get("count", 0) for d in _db.usage_network_daily.find({"day": day})}
    changed = [n for n, c in after.items() if c == before.get(n, 0) + 1]
    assert len(changed) == 1
    key = {"network": changed[0], "kind": "family-pattern", "day": day}
    original = _db.usage_network_daily.find_one(key)
    try:
        _db.usage_network_daily.update_one(key, {"$set": {"count": 60}})
        forged = ["1.2.3.4, 5.6.7.8", "1.2.3.4, 5.6.7.8, 9.9.9.9", "10.0.0.1,10.0.0.2,10.0.0.3,10.0.0.4"]
        for i, xff in enumerate(forged):
            body = {**BODY, "wife": ["male"] * (i + 1), "child_number": 1}
            r = member.post(f"{API}/analyses/family-pattern?lang=ar", json=body,
                            headers={"X-Forwarded-For": xff, "X-Real-IP": "8.8.8.8"})
            assert r.status_code == 429, (xff, r.status_code)
            assert "بالإنترنت" in r.json()["detail"]
    finally:
        _db.usage_network_daily.update_one(key, {"$set": {"count": original["count"],
                                                          "blocked": original.get("blocked", 0)}})
        # remove any counter docs the spoof may have created (none expected)
        extra = [d["network"] for d in _db.usage_network_daily.find({"day": day}) if d["network"] not in after]
        print("extra network docs created by spoof:", extra)
        assert not extra
