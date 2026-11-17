"""Daily limits for the protected family-pattern calculator, per account and per network connection.

Admin is never limited. Network addresses are stored only as a keyed hash. Blocked attempts are counted
(no personal data) so the admin can see possible copying attempts.
"""
import hashlib
import hmac
import os
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, Request
from pymongo.errors import DuplicateKeyError

from .db import db
from .i18n import t
from .protection import DAILY_LIMIT, PROTECTED_KIND

NETWORK_DAILY_LIMIT = 60
INFRA_HOPS = 2  # the ingress appends Cloudflare edge + load balancer after the real client address


def client_ip(request: Request) -> str:
    parts = [p.strip() for p in request.headers.get("x-forwarded-for", "").split(",") if p.strip()]
    if len(parts) > INFRA_HOPS:
        return parts[-INFRA_HOPS - 1]
    if parts:
        return parts[0]
    return request.client.host if request.client else "unknown"


def _network_id(ip: str) -> str:
    key = hashlib.sha256(f"genova-network:{os.environ['CLERK_SECRET_KEY']}".encode()).digest()
    return hmac.new(key, ip.encode(), hashlib.sha256).hexdigest()[:32]


def _today() -> str:
    return datetime.now(UTC).date().isoformat()


def limit_keys(member: dict, kind: str, request: Request) -> tuple[dict, dict] | None:
    if kind != PROTECTED_KIND or member["role"] == "admin":
        return None
    day = _today()
    return ({"user_id": member["user_id"], "kind": kind, "day": day},
            {"network": _network_id(client_ip(request)), "kind": kind, "day": day})


async def _block(coll: str, key: dict, message: str) -> None:
    await db[coll].update_one(key, {"$inc": {"blocked": 1}}, upsert=True)
    raise HTTPException(status_code=429, detail=message)


async def check_limits(keys: tuple[dict, dict] | None, lang: str) -> None:
    if not keys:
        return
    account, network = keys
    used = await db.usage_daily.find_one(account)
    if used and used.get("count", 0) >= DAILY_LIMIT:
        await _block("usage_daily", account, t("daily_limit_reached", lang))
    if not await _reserve(network):
        await _block("usage_network_daily", network, t("network_limit_reached", lang))


async def _reserve(network: dict) -> bool:
    """Atomic slot reservation: accounts sharing a connection cannot overshoot the limit concurrently."""
    for _ in range(2):  # a second try covers two first requests of the day racing to create the counter
        try:
            await db.usage_network_daily.update_one({**network, "count": {"$lt": NETWORK_DAILY_LIMIT}},
                                                    {"$inc": {"count": 1}}, upsert=True)
            return True
        except DuplicateKeyError:
            doc = await db.usage_network_daily.find_one(network)
            if doc and doc.get("count", 0) >= NETWORK_DAILY_LIMIT:
                return False
    return False


async def release_slot(keys: tuple[dict, dict] | None) -> None:
    if keys:
        await db.usage_network_daily.update_one(keys[1], {"$inc": {"count": -1}})


async def count_use(keys: tuple[dict, dict] | None) -> None:
    """The account count is kept under the per-account save lock; the connection slot was reserved on check."""
    if keys:
        await db.usage_daily.update_one(keys[0], {"$inc": {"count": 1}}, upsert=True)


async def _blocked_summary(coll: str, since: str) -> dict:
    rows = await db[coll].aggregate([
        {"$match": {"day": {"$gte": since}, "blocked": {"$gt": 0}}},
        {"$group": {"_id": None, "attempts": {"$sum": "$blocked"}, "hits": {"$sum": 1}}}]).to_list(None)
    return {"blocked_attempts": rows[0]["attempts"] if rows else 0, "limit_hits": rows[0]["hits"] if rows else 0}


async def limit_stats(days: int = 30) -> dict:
    since = (datetime.now(UTC).date() - timedelta(days=days - 1)).isoformat()
    return {"days": days, "account_limit": DAILY_LIMIT, "network_limit": NETWORK_DAILY_LIMIT,
            "accounts": await _blocked_summary("usage_daily", since),
            "networks": await _blocked_summary("usage_network_daily", since)}
