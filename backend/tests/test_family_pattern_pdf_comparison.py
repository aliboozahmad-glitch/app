# Read-only verification: PDF transcription vs current GENOVA family-pattern table/lookup
import json
import os
import subprocess
from pathlib import Path

import pytest
import requests
from dotenv import dotenv_values
from live_roles import as_role

from genova.traditional.family_pattern import family_pattern_analysis, load_table

ROOT = Path(__file__).resolve().parents[2]
PDF = json.loads((ROOT / "docs/source/pdf_transcription.json").read_text(encoding="utf-8"))
G = {"M": "male", "F": "female"}
BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL")
            or dotenv_values(ROOT / "frontend/.env")["REACT_APP_BACKEND_URL"]).rstrip("/")


def _genova(e, child=1):
    r = family_pattern_analysis([G[x] for x in e["wife"]], [G[x] for x in e["husband"]], child)
    return (r["outcomes"][0]["key"] if r["outcomes"] else None), r["details"]


def _pdf(e, child=1):
    res = e["result"]
    if "single" in res:
        return G[res["single"]]
    return G[res["first" if child == 1 else "second"]]


# Entry count / numbering
def test_pdf_entry_count_and_numbers():
    nums = [e["case"] for e in PDF]
    assert len(PDF) == 81
    assert nums == list(range(1, 30)) + list(range(41, 93))
    pages = {p: [e["case"] for e in PDF if e["page"] == p] for p in (1, 2, 3)}
    assert pages[1] == list(range(1, 30)) and pages[2] == list(range(41, 68)) and pages[3] == list(range(68, 93))


def test_pdf_pairs_unique():
    keys = [(tuple(e["wife"]), tuple(e["husband"])) for e in PDF]
    assert len(set(keys)) == 81


def test_case_71_correction():
    e = next(x for x in PDF if x["case"] == 71)
    assert e["wife"] == ["F"] and e["husband"] == ["F", "M", "F"] and e["result"] == {"single": "F"}


def test_genova_table_count_and_extras():
    t = load_table()
    cases = [c["case"] for c in t["cases"]]
    assert len(cases) == 78 and not set(cases) - {e["case"] for e in PDF}
    assert {e["case"] for e in PDF} - set(cases) == {84, 87, 92}
    assert [c["case"] for c in t["old_app_only_cases"]] == list(range(30, 41))


# Section 1: exact match on families and both results
@pytest.mark.parametrize("e", [x for x in PDF if x["case"] <= 29], ids=lambda e: f"case{e['case']}")
def test_section1_matches(e):
    table = {c["case"]: c for c in load_table()["cases"]}
    c = table[e["case"]]
    assert c["wife"] == [G[x] for x in e["wife"]] and c["husband"] == [G[x] for x in e["husband"]]
    for child in (1, 2):
        assert _genova(e, child)[0] == _pdf(e, child)


# Section 2: 41-60, 69-80 match by case number + families + result
@pytest.mark.parametrize("e", [x for x in PDF if 41 <= x["case"] <= 60 or 69 <= x["case"] <= 80],
                         ids=lambda e: f"case{e['case']}")
def test_section2_listed_match(e):
    table = {c["case"]: c for c in load_table()["cases"]}
    c = table[e["case"]]
    assert c["wife"] == [G[x] for x in e["wife"]] and c["husband"] == [G[x] for x in e["husband"]]
    assert c["result"]["first"] == c["result"]["second"] == _pdf(e)
    assert _genova(e)[0] == _pdf(e)


EXPECTED_DIFF = {84: "male", 87: "female", 92: None}


@pytest.mark.parametrize("e", [x for x in PDF if 61 <= x["case"] <= 68 or x["case"] >= 81],
                         ids=lambda e: f"case{e['case']}")
def test_missing_ranges_current_behaviour(e):
    got, _ = _genova(e)
    if e["case"] in EXPECTED_DIFF:
        assert got == EXPECTED_DIFF[e["case"]] and got != _pdf(e)
    else:
        assert got == _pdf(e)


def test_results_table_flagged_unchanged():
    assert load_table()["results_changed"] is False


# API: same answers via POST /api/analyses/family-pattern
@pytest.fixture(scope="module")
def token():
    r = subprocess.run(["python", str(ROOT / "scripts/clerk_test_session.py")], capture_output=True, text=True)
    try:
        tok = json.loads(r.stdout)["token"]
    except (ValueError, KeyError):
        pytest.skip("no clerk token")
    sess = requests.Session()
    sess.headers["Authorization"] = f"Bearer {tok}"
    with as_role(sess, f"{BASE_URL}/api", "admin"):
        yield tok


@pytest.mark.parametrize("case", [84, 87, 92])
def test_api_matches_function(token, case):
    e = next(x for x in PDF if x["case"] == case)
    body = {"wife": [G[x] for x in e["wife"]], "husband": [G[x] for x in e["husband"]], "child_number": 1}
    r = requests.post(f"{BASE_URL}/api/analyses/family-pattern", json=body,
                      headers={"Authorization": f"Bearer {token}"}, timeout=30)
    assert r.status_code == 200, r.text
    data = r.json()
    if data.get("id"):
        requests.delete(f"{BASE_URL}/api/analyses/{data['id']}", headers={"Authorization": f"Bearer {token}"},
                        timeout=30)
    res = data.get("result", data)
    outs = res["outcomes"]
    api = outs[0]["key"] if outs else None
    assert api == _genova(e)[0]


@pytest.mark.parametrize("e", [x for x in PDF if 61 <= x["case"] <= 68 or x["case"] >= 81 and x["case"] not in (84, 87, 92)],
                         ids=lambda e: f"case{e['case']}")
def test_pdf_only_entries_copied_exactly(e):
    c = {c["case"]: c for c in load_table()["cases"]}[e["case"]]
    assert c["wife"] == [G[x] for x in e["wife"]] and c["husband"] == [G[x] for x in e["husband"]]
    assert c["pdf_result"]["single"] == _pdf(e) and c["origin"] == "original_pdf"
