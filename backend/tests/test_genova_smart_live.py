"""GENOVA Smart Algorithm through the live API: PDF answers only, owner-confirmed 84/87/92, no fallback."""
import json
import os
import subprocess
import time
from pathlib import Path

import pytest
import requests
from dotenv import dotenv_values
from live_roles import as_role

ROOT = Path(__file__).resolve().parents[2]
BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL")
            or dotenv_values(ROOT / "frontend/.env")["REACT_APP_BACKEND_URL"]).rstrip("/")
API = f"{BASE_URL}/api"
PDF = {e["case"]: e for e in json.loads((ROOT / "docs/source/pdf_transcription.json").read_text(encoding="utf-8"))}
G = {"M": "male", "F": "female"}


def _session():
    out = subprocess.run(["python", str(ROOT / "scripts/clerk_test_session.py"), "genova.smart+clerk_test@example.com"],
                         capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        pytest.skip("clerk session failed")
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {json.loads(out.stdout)['token']}"
    return s


@pytest.fixture(scope="module")
def admin():
    s = _session()
    with as_role(s, API, "admin"):
        yield s
    for item in s.get(f"{API}/analyses").json()["items"]:
        s.delete(f"{API}/analyses/{item['id']}")


@pytest.fixture(scope="module")
def member():
    s = _session()
    with as_role(s, API, "member"):
        yield s


def _body(case, child=None):
    e = PDF[case]
    body = {"wife": [G[x] for x in e["wife"]], "husband": [G[x] for x in e["husband"]]}
    return {**body, "child_number": child} if child else body


@pytest.mark.parametrize("case,answer", [(84, "female"), (87, "male"), (92, "male")])
def test_owner_confirmed_cases(admin, case, answer):
    r = admin.post(f"{API}/analyses/family-pattern", json=_body(case)).json()["result"]
    assert [(o["key"], o["stated_range"]) for o in r["outcomes"]] == [(answer, "90%")]
    assert r["details"]["effective_case"] == case and r["details"]["case_source"] == "original_pdf_owner_confirmed"


@pytest.mark.parametrize("case", [1, 17, 29, 41, 53, 61, 68, 71, 81, 91])
def test_pdf_cases_answered_exactly(admin, case):
    e = PDF[case]
    child = 2 if case <= 29 else None
    r = admin.post(f"{API}/analyses/family-pattern", json=_body(case, child)).json()["result"]
    expected = G[e["result"]["second"]] if child else G[e["result"]["single"]]
    assert [o["key"] for o in r["outcomes"]] == [expected] and r["details"]["effective_case"] == case
    time.sleep(1)


@pytest.mark.parametrize("wife,husband,child", [
    (["male"], ["female"], None),  # old-app case 37
    (["female", "female", "male"], ["male", "female", "male"], 1),  # old-app case 30
    (["male"], ["male", "male", "female"], None),  # old borrowed answer, not in the PDF
])
def test_no_matching_case_for_member(member, wife, husband, child):
    body = {"wife": wife, "husband": husband, **({"child_number": child} if child else {})}
    d = member.post(f"{API}/analyses/family-pattern?lang=de", json=body).json()
    assert d["result"]["outcomes"] == []
    assert "Kein passender Fall gefunden." in [n["text"] for n in d["result"]["limitations"]]
    assert d["result"]["method_label"] == "GENOVA Smart-Algorithmus"
    member.delete(f"{API}/analyses/{d['id']}")
