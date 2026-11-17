"""IP protection: ordinary members see only the answer, an approved range, date, short ID and a disclaimer."""
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest
import requests
from dotenv import dotenv_values
from live_roles import as_role, set_daily

BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL")
            or dotenv_values(Path("/app/frontend/.env"))["REACT_APP_BACKEND_URL"]).rstrip("/")
API = f"{BASE_URL}/api"
EMAIL = "genova.ip+clerk_test@example.com"
SECRET_KEYS = ("matched_cases", "effective_case", "source_case", "review_flags", "section", "origin", "wife",
               "husband", "pattern", "legacy-family-pattern-table", "gender_prediction_logic", "answer_borrowed",
               "data_version", "engine_version")


@pytest.fixture(scope="module")
def created():
    return set()


@pytest.fixture(scope="module")
def session():
    out = subprocess.run(["python", "/app/scripts/clerk_test_session.py", EMAIL], capture_output=True, text=True,
                         timeout=60)
    if out.returncode != 0:
        pytest.skip("clerk session failed")
    sess = requests.Session()
    sess.headers["Authorization"] = f"Bearer {json.loads(out.stdout)['token']}"
    return sess


@pytest.fixture(scope="module")
def member(session, created):
    with as_role(session, API, "member") as uid:
        session.uid = uid
        yield session
    for i in created:
        session.delete(f"{API}/analyses/{i}")


def _post(s, created, body, lang="en"):
    r = s.post(f"{API}/analyses/family-pattern?lang={lang}", json=body)
    if r.status_code == 200:
        created.add(r.json()["id"])
    return r


def _no_secrets(payload):
    text = json.dumps(payload, ensure_ascii=False)
    for k in SECRET_KEYS:
        cleaned = text.replace('"family-pattern"', "").replace("family_pattern", "")
        assert f'"{k}"' not in cleaned and f"{k}:" not in cleaned, k
    for name in ("genova-smart-pdf", "legacy-family-pattern-table", "gender_prediction_logic", "case_source", "pdf_page"):
        assert name not in text, name


@pytest.mark.parametrize("lang", ["en", "ar", "de"])
def test_single_child_public_shape(member, created, lang):
    r = _post(member, created, {"wife": ["male", "male", "female"], "husband": ["female"]}, lang)  # PDF 86
    assert r.status_code == 200, r.text
    d = r.json()
    _no_secrets(d)
    assert d["request"] == {} and d["report_id"] == f"GN-{d['id'][-8:].upper()}"
    res = d["result"]
    assert res["public"] is True and res["details"] == {} and res["references"] == [] and res["inputs"] == {}
    assert [(o["key"], o["stated_range"]) for o in res["outcomes"]] == [("male", None)]
    assert [n["key"] for n in res["limitations"]] == ["traditional_public_disclaimer"]


def test_three_plus_three_shows_stated_range(member, created):
    w, h = ["male", "male", "female"], ["female", "male", "female"]
    first = _post(member, created, {"wife": w, "husband": h, "child_number": 1}).json()["result"]["outcomes"][0]
    second = _post(member, created, {"wife": w, "husband": h, "child_number": 2}).json()["result"]["outcomes"][0]
    assert (first["key"], first["stated_range"]) == ("male", "70\u201390%")
    assert (second["key"], second["stated_range"]) == ("female", "50\u201360%")


def test_not_in_table_public(member, created):
    d = _post(member, created, {"wife": ["male"], "husband": ["female"]}).json()  # old-app case 37, not in PDF
    _no_secrets(d)
    assert d["result"]["outcomes"] == []
    assert [n["key"] for n in d["result"]["limitations"]] == ["traditional_public_disclaimer", "no_result_available"]


def test_history_list_and_detail_protected(member, created):
    items = [i for i in member.get(f"{API}/analyses").json()["items"] if i["analysis_type"] == "family-pattern"]
    assert items and all(i["request"] == {} for i in items)
    _no_secrets(items)
    detail = member.get(f"{API}/analyses/{items[0]['id']}?lang=ar").json()
    _no_secrets(detail)
    assert detail["result"]["public"] is True


def test_public_references_hide_internal_table():
    refs = requests.get(f"{API}/references", timeout=30).json()["references"]
    assert "legacy-family-pattern-table" not in [r["id"] for r in refs]


def test_admin_still_sees_details(session, created):
    with as_role(session, API, "admin"):
        d = _post(session, created, {"wife": ["male", "female", "male"], "husband": ["female"]}).json()
    assert d["result"].get("public") is None and d["result"]["details"]["effective_case"] == 84


def test_daily_limit_20(member, created):
    day = datetime.now(UTC).date().isoformat()
    set_daily(member.uid, "family-pattern", day, 20)
    r = _post(member, created, {"wife": ["female"], "husband": ["female", "male", "female"]}, "de")
    assert r.status_code == 429 and "20" in r.json()["detail"]
    set_daily(member.uid, "family-pattern", day, 19)
    assert _post(member, created, {"wife": ["female"], "husband": ["female", "male", "female"]}).status_code == 200
