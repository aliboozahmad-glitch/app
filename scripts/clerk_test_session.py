"""Dev-only helper: create (or reuse) a Clerk test user and print a sign-in ticket + session token.
Usage: python /app/scripts/clerk_test_session.py [email]
Never run against a live (pk_live_) instance."""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

from dotenv import load_dotenv

load_dotenv("/app/backend/.env")
SK = os.environ["CLERK_SECRET_KEY"]
assert SK.startswith("sk_test_"), "development instance only"


def bapi(path, body=None, method="POST"):
    req = urllib.request.Request("https://api.clerk.com/v1" + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": "Bearer " + SK, "Content-Type": "application/json",
                                          "User-Agent": "emergent-test"})
    return json.load(urllib.request.urlopen(req))


email = sys.argv[1] if len(sys.argv) > 1 else "genova.tester+clerk_test@example.com"
found = bapi("/users?" + urllib.parse.urlencode({"email_address": email}), method="GET")
user = found[0] if found else bapi("/users", {"email_address": [email], "password": "Genova-Test-2026!",
                                              "skip_password_checks": True})
session = bapi("/sessions", {"user_id": user["id"]})
token = bapi(f"/sessions/{session['id']}/tokens", {"expires_in_seconds": 3600})["jwt"]
ticket = bapi("/sign_in_tokens", {"user_id": user["id"], "expires_in_seconds": 3600})["token"]
print(json.dumps({"user_id": user["id"], "email": email, "token": token, "ticket": ticket}))
