"""Daily-limit edge cases for family-pattern: errors, dedupe, delete, admin exemption, localization."""
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest
import requests
from dotenv import dotenv_values
from live_roles import _db, as_role, set_daily

BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL")
            or dotenv_values(Path("/app/frontend/.env"))["REACT_APP_BACKEND_URL"]).rstrip("/")
API = f"{BASE_URL}/api"
EMAIL = "genova.ip+clerk_test@example.com"
DAY = datetime.now(UTC).date().isoformat()


def _count(uid):
    d = _db.usage_daily.find_one({"user_id": uid, "kind": "family-pattern", "day": DAY})
    return d["count"] if d else 0


@pytest.fixture(scope="module")
def session():
    out = subprocess.run(["python", "/app/scripts/clerk_test_session.py", EMAIL], capture_output=True, text=True,
                         timeout=60)
    if out.returncode != 0:
        pytest.skip("clerk session failed")
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {json.loads(out.stdout)['token']}"
    return s


@pytest.fixture(scope="module")
def created():
    return set()


@pytest.fixture(autouse=True, scope="module")
def cleanup(session, created):
    yield
    for i in created:
        session.delete(f"{API}/analyses/{i}")


def _post(s, created, body, lang="en"):
    r = s.post(f"{API}/analyses/family-pattern?lang={lang}", json=body)
    if r.status_code == 200:
        created.add(r.json()["id"])
    return r


# Input error (3+3 without child_number) should not consume the daily quota
def test_error_does_not_count(session, created):
    with as_role(session, API, "member") as uid:
        r = _post(session, created, {"wife": ["male", "male", "female"], "husband": ["female", "male", "female"]})
        assert r.status_code == 400, r.text
        assert _count(uid) == 0, f"failed request counted: {_count(uid)}"


# Dedupe does not count; delete does not reset
def test_dedupe_and_delete(session, created):
    with as_role(session, API, "member") as uid:
        body = {"wife": ["female", "female"], "husband": ["male"]}
        a = _post(session, created, body)
        assert a.status_code == 200
        b = _post(session, created, body)
        assert b.json().get("deduplicated") is True and b.json()["id"] == a.json()["id"]
        assert _count(uid) == 1
        session.delete(f"{API}/analyses/{a.json()['id']}")
        assert _count(uid) == 1


# 429 message localized in ar/de
@pytest.mark.parametrize("lang", ["en", "ar", "de"])
def test_429_localized(session, created, lang):
    with as_role(session, API, "member") as uid:
        set_daily(uid, "family-pattern", DAY, 20)
        r = _post(session, created, {"wife": ["male"], "husband": ["male", "male"]}, lang)
        assert r.status_code == 429
        print(lang, r.json()["detail"])
        assert "20" in r.json()["detail"]
        assert _count(uid) == 20


# Admin exempt
def test_admin_exempt(session, created):
    with as_role(session, API, "admin") as uid:
        set_daily(uid, "family-pattern", DAY, 25)
        r = _post(session, created, {"wife": ["male"], "husband": ["female", "female"]})
        assert r.status_code == 200 and r.json()["result"]["details"]


# Other calculators not limited at 20
def test_other_calculators_unlimited(session, created):
    with as_role(session, API, "member") as uid:
        set_daily(uid, "family-pattern", DAY, 20)
        r = session.post(f"{API}/analyses/blood-type", json={"parent1_abo": "A", "parent1_rh": "+", "parent2_abo": "B", "parent2_rh": "-"})
        print(r.status_code, r.text[:200])
        assert r.status_code == 200
        if r.status_code == 200:
            created.add(r.json()["id"])
