"""Test-only CLI used by UI security checks: tickets, network counter snapshot/set/restore, role switch."""
import json
import subprocess
import sys
from datetime import UTC, datetime

from live_roles import _db

STATE = "/tmp/ui_sec_state.json"
day = datetime.now(UTC).date().isoformat()
cmd = sys.argv[1]
if cmd == "ticket":
    out = json.loads(subprocess.run(["python", "/app/scripts/clerk_test_session.py", sys.argv[2]],
                                    capture_output=True, text=True, timeout=60).stdout)
    print(out["ticket"])
elif cmd == "snap":
    json.dump({d["network"]: d.get("count", 0) for d in _db.usage_network_daily.find({"day": day})}, open(STATE, "w"))
    print("snap ok")
elif cmd == "find":
    before = json.load(open(STATE))
    after = {d["network"]: d.get("count", 0) for d in _db.usage_network_daily.find({"day": day})}
    changed = [n for n, c in after.items() if c > before.get(n, 0)]
    print("changed:", changed)
    doc = _db.usage_network_daily.find_one({"network": changed[0], "day": day, "kind": "family-pattern"}, {"_id": 0})
    json.dump(doc, open(STATE + ".orig", "w"))
    print("orig", doc)
elif cmd == "set":
    doc = json.load(open(STATE + ".orig"))
    _db.usage_network_daily.update_one({k: doc[k] for k in ("network", "kind", "day")},
                                       {"$set": {"count": int(sys.argv[2])}})
    print(_db.usage_network_daily.find_one({k: doc[k] for k in ("network", "kind", "day")}, {"_id": 0}))
elif cmd == "show":
    doc = json.load(open(STATE + ".orig"))
    print(_db.usage_network_daily.find_one({k: doc[k] for k in ("network", "kind", "day")}, {"_id": 0}))
elif cmd == "restore":
    doc = json.load(open(STATE + ".orig"))
    key = {k: doc[k] for k in ("network", "kind", "day")}
    cur = _db.usage_network_daily.find_one(key)
    _db.usage_network_daily.update_one(key, {"$set": {"count": doc["count"] + int(sys.argv[2] if len(sys.argv) > 2 else 0),
                                                      "blocked": doc.get("blocked", 0)}})
    print("was", {k: cur.get(k) for k in ("count", "blocked")}, "now", _db.usage_network_daily.find_one(key, {"_id": 0}))
elif cmd == "role":
    email, role = sys.argv[2], sys.argv[3]
    u = _db.users.find_one({"email": email}, {"_id": 0, "role": 1, "user_id": 1})
    print("before", u)
    _db.users.update_one({"email": email}, {"$set": {"role": role}})
    print("after", _db.users.find_one({"email": email}, {"_id": 0, "role": 1}))
