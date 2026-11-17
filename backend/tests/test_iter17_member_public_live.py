"""Iteration 17: member public family-pattern view (no case number), 3+3 ranges, no-match, admin case number."""
import json
import os
import subprocess
from pathlib import Path

import pytest
import requests
from live_roles import as_role

ROOT = Path(__file__).resolve().parents[2]
API = f"{os.environ['REACT_APP_BACKEND_URL'].rstrip('/')}/api"
M, F = "male", "female"


def _session(email):
    out = subprocess.run(["python", str(ROOT / "scripts/clerk_test_session.py"), email],
                         capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        pytest.skip("clerk session failed")
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {json.loads(out.stdout)['token']}"
    return s


@pytest.fixture(scope="module")
def member():
    s = _session("genova.tester+clerk_test@example.com")
    with as_role(s, API, "member"):
        yield s


@pytest.fixture(scope="module")
def admin():
    s = _session("genova.tester+clerk_test@example.com")
    with as_role(s, API, "admin"):
        yield s


def _post(s, body):
    r = s.post(f"{API}/analyses/family-pattern", json=body)
    assert r.status_code in (200, 201), r.text
    d = r.json()
    s.delete(f"{API}/analyses/{d['id']}")
    return d


# Member: owner-confirmed cases, public view has no case number / details
@pytest.mark.parametrize("wife,husband,ans", [([M, F, M], [F], F), ([F, M, F], [M], M), ([M, F, F], [M], M)])
def test_member_confirmed(member, wife, husband, ans):
    d = _post(member, {"wife": wife, "husband": husband})
    raw = json.dumps(d)
    assert "effective_case" not in raw and "pdf_page" not in raw and "case_source" not in raw
    assert d["result"]["details"] == {} and d["result"]["references"] == []
    assert [(o["key"], o.get("stated_range")) for o in d["result"]["outcomes"]] == [(ans, "90%")]


# Member: 3+3 PDF case ranges
@pytest.mark.parametrize("child,ans,rng", [(1, M, "70–90%"), (2, F, "50–60%")])
def test_member_three_three(member, child, ans, rng):
    d = _post(member, {"wife": [M, M, F], "husband": [F, M, F], "child_number": child})
    assert [(o["key"], o.get("stated_range")) for o in d["result"]["outcomes"]] == [(ans, rng)]


# Member: Boy-Boy-Boy | Boy-Boy-Boy -> no match
def test_member_no_match_bbb(member):
    d = _post(member, {"wife": [M, M, M], "husband": [M, M, M], "child_number": 1})
    assert d["result"]["outcomes"] == []


# Admin: case 84 shows effective_case; non-match has no effective_case
def test_admin_case_84_and_no_match(admin):
    d = _post(admin, {"wife": [M, F, M], "husband": [F]})
    assert d["result"]["details"]["effective_case"] == 84
    d2 = _post(admin, {"wife": [M], "husband": [F]})
    assert d2["result"]["outcomes"] == [] and "effective_case" not in d2["result"]["details"]
    assert "no_matching_case" in d2["result"]["details"]["review_flags"]
