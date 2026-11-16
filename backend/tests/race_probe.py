"""Manual probe (not collected by pytest): fire N truly-concurrent identical POSTs and count distinct ids."""
import json
import random
import subprocess
import sys
import threading
from pathlib import Path

import requests
from dotenv import dotenv_values

API = dotenv_values(Path("/app/frontend/.env"))["REACT_APP_BACKEND_URL"].rstrip("/") + "/api"
email = sys.argv[1] if len(sys.argv) > 1 else "genova.other+clerk_test@example.com"
n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
tok = json.loads(subprocess.run(["python", "/app/scripts/clerk_test_session.py", email],
                                capture_output=True, text=True, check=True).stdout)["token"]
body = {"mother_cm": round(random.uniform(150, 180), 1), "father_cm": round(random.uniform(160, 200), 1)}
barrier = threading.Barrier(n)
res = []


def go():
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {tok}"
    s.get(API + "/health")  # warm connection
    barrier.wait()
    r = s.post(API + "/analyses/height", json=body)
    res.append((r.status_code, r.json().get("id"), r.json().get("deduplicated")))


ts = [threading.Thread(target=go) for _ in range(n)]
[t.start() for t in ts]
[t.join() for t in ts]
print(res)
ids = {i for _, i, _ in res if i}
print("distinct ids:", len(ids))
s = requests.Session()
s.headers["Authorization"] = f"Bearer {tok}"
for i in ids:
    print("cleanup", i, s.delete(f"{API}/analyses/{i}").status_code)
