"""Emergent-managed Clerk auth, inert until CLERK_PUBLISHABLE_KEY/CLERK_SECRET_KEY
are set: /api/clerk/config for the frontend, the /api/__clerk production relay
(zero DNS per app), and the require_user dependency for protected routes."""

import base64
import os
from functools import lru_cache

import jwt
import requests
from fastapi import APIRouter, HTTPException, Request, Response
from requests.adapters import HTTPAdapter
from starlette.concurrency import run_in_threadpool
from urllib3.util.retry import Retry

CLERK_FRONTEND_API = "https://frontend-api.clerk.dev"
CLERK_BACKEND_API = "https://api.clerk.com/v1"
PROXY_PATH = "/api/__clerk"

# Per-hop headers are never relayed; requests decodes the body, so its encoding goes too.
_HOP_HEADERS = {
    "host", "connection", "keep-alive", "content-length", "transfer-encoding",
    "te", "trailer", "upgrade", "proxy-authorization", "proxy-authenticate",
    "content-encoding",
}

clerk_router = APIRouter(prefix="/api")
_http = requests.Session()
# Clerk's edge closes idle keep-alive connections; retry idempotent calls on a dropped one.
_retry = Retry(total=2, connect=2, read=2, status=0, backoff_factor=0.1,
               allowed_methods=frozenset({"GET", "HEAD", "OPTIONS"}))
_http.mount("https://", HTTPAdapter(pool_maxsize=40, max_retries=_retry))  # matches the threadpool size


def _publishable_key() -> str:
    return os.environ.get("CLERK_PUBLISHABLE_KEY", "")


def _secret_key() -> str:
    return os.environ.get("CLERK_SECRET_KEY", "")


def _is_production() -> bool:
    # Only production instances are served through the /api/__clerk proxy.
    return _publishable_key().startswith("pk_live_")


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else ""


@clerk_router.get("/clerk/config")
def clerk_config():
    """What the frontend needs to start Clerk (the publishable key is public)."""
    key = _publishable_key()
    return {
        "enabled": bool(key and _secret_key()),
        "publishable_key": key,
        "proxy_url": PROXY_PATH if _is_production() else "",
    }


@clerk_router.api_route("/__clerk/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def clerk_proxy(path: str, request: Request):
    """Relay Clerk's Frontend API through this app's own domain."""
    if not _is_production():
        raise HTTPException(status_code=404)
    host = request.headers.get("x-forwarded-host") or request.headers.get("host", "")
    headers = {k: v for k, v in request.headers.items() if k.lower() not in _HOP_HEADERS}
    headers["Clerk-Proxy-Url"] = f"https://{host.split(',')[0].strip()}{PROXY_PATH}"
    headers["Clerk-Secret-Key"] = _secret_key()
    headers["X-Forwarded-For"] = _client_ip(request)
    headers["Accept-Encoding"] = "gzip"  # requests cannot decode brotli

    try:
        upstream = await run_in_threadpool(
            _http.request,
            request.method,
            f"{CLERK_FRONTEND_API}/{path}",
            params=list(request.query_params.multi_items()),
            headers=headers,
            data=await request.body(),
            allow_redirects=False,
            timeout=30,
        )
    except requests.RequestException:
        # Clerk's frontend retries a 502; an unhandled error would be a bare 500.
        return Response(status_code=502)
    response = Response(content=upstream.content, status_code=upstream.status_code)
    raw = upstream.raw.headers
    for name in {n.lower() for n in raw.keys()} - _HOP_HEADERS:
        # getlist keeps every Set-Cookie separate; joining them breaks sessions.
        for value in raw.getlist(name):
            response.raw_headers.append((name.encode(), value.encode()))
    return response


@lru_cache(maxsize=1)
def _jwks_client(secret_key: str) -> jwt.PyJWKClient:
    # Caches Clerk's signing keys and refetches when it meets a new key id.
    return jwt.PyJWKClient(
        f"{CLERK_BACKEND_API}/jwks",
        # Clerk's edge rejects urllib's default User-Agent (Cloudflare 1010).
        headers={"Authorization": f"Bearer {secret_key}", "User-Agent": "emergent-clerk-auth"},
        lifespan=3600,
        timeout=10,
    )


REQUIRED_CLAIMS = ["exp", "nbf", "iat", "iss", "sub", "sid"]


def _instance_issuer() -> str:
    """Clerk's Frontend API URL, encoded in the publishable key as base64("<host>$")."""
    encoded = _publishable_key().split("_", 2)[2]
    host = base64.b64decode(encoded + "=" * (-len(encoded) % 4)).decode().removesuffix("$").strip().rstrip("/")
    return f"https://{host}"


def _app_origins(request: Request) -> set[str]:
    hosts = request.headers.get("x-forwarded-host") or request.headers.get("host", "")
    return {f"https://{h.strip()}" for h in hosts.split(",") if h.strip()}


def _allowed_issuers(request: Request) -> set[str]:
    issuers = {_instance_issuer()}
    if _is_production():  # tokens issued through this app's own Clerk relay
        issuers |= {f"{origin}{PROXY_PATH}" for origin in _app_origins(request)}
    return issuers


def _check_party(claims: dict, request: Request) -> None:
    """azp is the browser origin that obtained the token; it must be this app. Tokens without azp exist
    only when minted with the secret key (dev test tooling) and are refused on production instances."""
    azp = claims.get("azp")
    if azp is None and not _is_production():
        return
    if not isinstance(azp, str) or azp.rstrip("/") not in _app_origins(request):
        raise jwt.InvalidTokenError("unexpected authorized party")


def verify_session_token(token: str, request: Request) -> dict:
    """Return the verified claims of a Clerk session token, or raise 401.
    Checks: RS256 signature from this instance's JWKS, exp/nbf/iat, issuer, authorized party.
    Clerk session tokens carry no audience claim, so azp is the audience check."""
    try:
        if jwt.get_unverified_header(token).get("alg") != "RS256":
            raise jwt.InvalidTokenError("unexpected algorithm")
        key = _jwks_client(_secret_key()).get_signing_key_from_jwt(token).key
        claims = jwt.decode(token, key=key, algorithms=["RS256"], leeway=5,
                            options={"require": REQUIRED_CLAIMS, "verify_aud": False})
        if claims["iss"] not in _allowed_issuers(request):
            raise jwt.InvalidIssuerError("unexpected issuer")
        _check_party(claims, request)
        return claims
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired session") from exc


def require_user(request: Request) -> dict:
    """FastAPI dependency: the signed-in user from `Authorization: Bearer`
    (frontend getToken()) or Clerk's `__session` cookie; user["user_id"] is stable."""
    if not _secret_key():
        raise HTTPException(status_code=503, detail="Clerk is not configured")
    auth = request.headers.get("authorization", "")
    token = auth[7:] if auth.lower().startswith("bearer ") else request.cookies.get("__session", "")
    if not token:
        raise HTTPException(status_code=401, detail="Not signed in")
    claims = verify_session_token(token, request)
    return {"user_id": claims["sub"], "session_id": claims.get("sid"), "claims": claims}
