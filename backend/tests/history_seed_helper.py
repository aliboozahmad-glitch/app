"""Manual helper: create TEST analyses for the history-summary UI check (prints ids) or delete given ids."""
import json
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import dotenv_values

API = dotenv_values(Path("/app/frontend/.env"))["REACT_APP_BACKEND_URL"].rstrip("/") + "/api"
tok = json.loads(subprocess.run(["python", "/app/scripts/clerk_test_session.py"], capture_output=True, text=True,
                                check=True).stdout)["token"]
s = requests.Session()
s.headers["Authorization"] = f"Bearer {tok}"
if sys.argv[1:2] == ["delete"]:
    for i in sys.argv[2:]:
        print(i, s.delete(f"{API}/analyses/{i}").status_code)
    sys.exit()
dis = next(d["id"] for d in s.get(API + "/catalog").json()["diseases"] if d["inheritance"] == "autosomal_recessive")
bodies = {"mendelian": {"mode": "autosomal_recessive", "parent1": "Aa", "parent2": "Aa"},
          "carrier-risk": {"disease_id": dis, "mother_status": "carrier", "father_status": "unknown", "region": "gulf"},
          "pigmentation": {"trait": "eye_color", "mother": "brown", "father": "blue"}}
out = {k: s.post(f"{API}/analyses/{k}", json=b).json()["id"] for k, b in bodies.items()}
print(json.dumps(out))
