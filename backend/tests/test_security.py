"""Security unit tests: strict Clerk token checks, route authorization inventory, client address parsing."""
import base64
import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from starlette.requests import Request

import clerk_auth
from genova.auth import current_member
from genova.limits import client_ip

PK_HOST = "star-test-1.clerk.accounts.dev"
APP = "genova.example.com"
KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
PUBLIC_ROUTES = {"/api/health", "/api/catalog", "/api/references", "/api/clerk/config", "/api/__clerk/{path:path}"}


class _Signing:
    key = KEY.public_key()


class _Jwks:
    def get_signing_key_from_jwt(self, _token):
        return _Signing()


@pytest.fixture(autouse=True)
def clerk_env(monkeypatch):
    def set_instance(prefix):
        monkeypatch.setenv("CLERK_PUBLISHABLE_KEY", prefix + base64.b64encode(f"{PK_HOST}$".encode()).decode())
    monkeypatch.setenv("CLERK_SECRET_KEY", "sk_test_unit")
    set_instance("pk_test_")
    monkeypatch.setattr(clerk_auth, "_jwks_client", lambda _secret: _Jwks())
    return set_instance


def _request(xff="", host=APP):
    headers = [(b"host", host.encode())]
    if xff:
        headers.append((b"x-forwarded-for", xff.encode()))
    return Request({"type": "http", "headers": headers, "client": ("10.0.0.1", 1), "method": "GET", "path": "/"})


def _token(alg="RS256", key=KEY, drop=(), **over):
    now = int(time.time())
    claims = {"iss": f"https://{PK_HOST}", "azp": f"https://{APP}", "sub": "user_1", "sid": "sess_1",
              "iat": now, "nbf": now - 1, "exp": now + 60, **over}
    for k in drop:
        claims.pop(k)
    return jwt.encode(claims, "x" * 32 if alg == "HS256" else key, algorithm=alg)


def test_valid_token_accepted():
    assert clerk_auth.verify_session_token(_token(), _request())["sub"] == "user_1"


@pytest.mark.parametrize("token", [
    _token(iss="https://evil.clerk.accounts.dev"),
    _token(azp="https://evil.example.com"),
    _token(exp=int(time.time()) - 60),
    _token(nbf=int(time.time()) + 120),
    _token(drop=("exp",)), _token(drop=("iat",)), _token(drop=("nbf",)), _token(drop=("sid",)),
    _token(alg="HS256"),
    _token(key=rsa.generate_private_key(public_exponent=65537, key_size=2048)),
], ids=["issuer", "azp", "expired", "not_yet_valid", "no_exp", "no_iat", "no_nbf", "no_sid", "hs256", "wrong_key"])
def test_invalid_tokens_rejected(token):
    with pytest.raises(HTTPException) as err:
        clerk_auth.verify_session_token(token, _request())
    assert err.value.status_code == 401


def test_missing_azp_only_allowed_on_dev_instance(clerk_env):
    assert clerk_auth.verify_session_token(_token(drop=("azp",)), _request())["sub"] == "user_1"
    clerk_env("pk_live_")
    with pytest.raises(HTTPException):
        clerk_auth.verify_session_token(_token(drop=("azp",)), _request())


def test_production_accepts_own_relay_issuer(clerk_env):
    clerk_env("pk_live_")
    claims = clerk_auth.verify_session_token(_token(iss=f"https://{APP}/api/__clerk"), _request())
    assert claims["sub"] == "user_1"


def _dependency_calls(dependant):
    for dep in dependant.dependencies:
        yield dep.call
        yield from _dependency_calls(dep)


def test_every_non_public_route_requires_sign_in():
    from server import app
    routes = [r for r in app.routes if getattr(r, "path", "").startswith("/api")]
    unprotected = [r.path for r in routes if r.path not in PUBLIC_ROUTES
                   and current_member not in set(_dependency_calls(r.dependant))]
    assert not unprotected, unprotected


def test_no_public_route_listing():
    from server import app
    assert (app.docs_url, app.redoc_url, app.openapi_url) == (None, None, None)


@pytest.mark.parametrize("xff,expected", [
    ("35.1.1.1,172.71.0.1,136.110.0.1", "35.1.1.1"),
    ("1.2.3.4,35.1.1.1,172.71.0.1,136.110.0.1", "35.1.1.1"),  # spoofed first entry is ignored
    ("35.1.1.1", "35.1.1.1"),
    ("", "10.0.0.1"),
])
def test_client_ip(xff, expected):
    assert client_ip(_request(xff)) == expected
