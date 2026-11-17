"""Test-only helpers: switch a live test user's role and reset its daily family-pattern counter."""
import os
from contextlib import contextmanager
from datetime import UTC, datetime

from pymongo import MongoClient

_db = MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]


def user_id(sess, api: str) -> str:
    return sess.get(f"{api}/me").json()["user_id"]


def reset_daily(uid: str) -> None:
    """Also clears today's per-connection counters: every live test shares this machine's connection."""
    _db.usage_daily.delete_many({"user_id": uid})
    _db.usage_network_daily.delete_many({"day": datetime.now(UTC).date().isoformat()})


def set_daily(uid: str, kind: str, day: str, count: int) -> None:
    _db.usage_daily.update_one({"user_id": uid, "kind": kind, "day": day}, {"$set": {"count": count}}, upsert=True)


@contextmanager
def as_role(sess, api: str, role: str, reset: bool = True):
    uid = user_id(sess, api)
    before = _db.users.find_one({"user_id": uid}, {"role": 1})["role"]
    _db.users.update_one({"user_id": uid}, {"$set": {"role": role}})
    if reset:
        reset_daily(uid)
    try:
        yield uid
    finally:
        _db.users.update_one({"user_id": uid}, {"$set": {"role": before}})
        if reset:
            reset_daily(uid)
