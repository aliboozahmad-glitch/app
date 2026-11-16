"""Roles stored in the app database, keyed by Clerk user_id. Checked on the server for every request."""
import os

import requests
from fastapi import Depends, HTTPException
from pymongo import ReturnDocument
from starlette.concurrency import run_in_threadpool

try:
    from backend.clerk_auth import require_user
except ModuleNotFoundError:
    from clerk_auth import require_user

from .db import db

ROLES = ["admin", "member"]
DEFAULT_ROLE = "member"
RETIRED_ROLES: dict = {}
RANK = {r: len(ROLES) - i for i, r in enumerate(ROLES)}

ENV = "live" if os.environ.get("CLERK_PUBLISHABLE_KEY", "").startswith("pk_live_") else "preview"
IN_ENV = {"env": {"$in": [ENV, None]}}


def effective_role(role) -> str:
    role = RETIRED_ROLES.get(role, role)
    return role if role in ROLES else DEFAULT_ROLE


def _clerk_user(user_id: str) -> dict:
    r = requests.get(f"https://api.clerk.com/v1/users/{user_id}", timeout=10,
                     headers={"Authorization": f"Bearer {os.environ['CLERK_SECRET_KEY']}", "User-Agent": "emergent-app"})
    r.raise_for_status()
    return r.json()


def _is_admin_email(clerk_user: dict) -> bool:
    admins = {e.strip().lower() for e in os.environ.get("ADMIN_EMAIL", "").split(",") if e.strip()}
    return any(e["email_address"].lower() in admins and (e.get("verification") or {}).get("status") == "verified"
               for e in clerk_user.get("email_addresses", []))


async def current_member(user: dict = Depends(require_user)) -> dict:
    uid = user["user_id"]
    member = await db.users.find_one({"user_id": uid}, {"_id": 0})
    if member is None or not member.get("role"):
        cu = await run_in_threadpool(_clerk_user, uid)
        role = "admin" if _is_admin_email(cu) else DEFAULT_ROLE
        email = next((e["email_address"] for e in cu.get("email_addresses", [])
                      if e.get("id") == cu.get("primary_email_address_id")), None)
        await db.users.update_one({"user_id": uid, "role": {"$in": [None, ""]}}, {"$set": {"role": role}})
        member = await db.users.find_one_and_update(
            {"user_id": uid}, {"$setOnInsert": {"user_id": uid, "role": role, "email": email}},
            upsert=True, projection={"_id": 0}, return_document=ReturnDocument.AFTER)
    if member.get("env") != ENV:
        await db.users.update_one({"user_id": uid}, {"$set": {"env": ENV}})
    return {**member, "env": ENV, "role": effective_role(member["role"])}


def require_role(*roles: str):
    async def check(member: dict = Depends(current_member)) -> dict:
        if member["role"] not in roles:
            raise HTTPException(status_code=403, detail="Not allowed")
        return member
    return check
