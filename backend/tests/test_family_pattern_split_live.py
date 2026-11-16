"""Live API tests: family-pattern wife/husband split (borrowed answers, old-app-only, baseline spot-check)."""
import json
import os
import random
import subprocess
import time
from pathlib import Path

import pytest
import requests
from dotenv import dotenv_values

BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL")
            or dotenv_values(Path("/app/frontend/.env"))["REACT_APP_BACKEND_URL"]).rstrip("/")
API = f"{BASE_URL}/api"
BASELINE = Path(__file__).parent / "fixtures" / "family_pattern_results_baseline.json"
M, F = "male", "female"


@pytest.fixture(scope="module")
def created():
    return set()


@pytest.fixture(scope="module")
def s(created):
    out = subprocess.run(["python", "/app/scripts/clerk_test_session.py"], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        pytest.skip("clerk session failed")
    sess = requests.Session()
    sess.headers["Authorization"] = f"Bearer {json.loads(out.stdout)['token']}"
    yield sess
    for i in created:
        sess.delete(f"{API}/analyses/{i}")


def _post(s, created, wife, husband, n=1, lang="en"):
    for _ in range(5):
        r = s.post(f"{API}/analyses/family-pattern?lang={lang}", json={"wife": wife, "husband": husband,
                                                                       "child_number": n})
        if r.status_code != 429:
            break
        time.sleep(15)
    assert r.status_code == 200, r.text
    d = r.json()
    if d.get("id"):
        created.add(d["id"])
    return d.get("result", d)


def _key(res):
    return res["outcomes"][0]["key"] if res["outcomes"] else None


# Borrowed answer from case 75
def test_borrowed_75(s, created):
    res = _post(s, created, [M, F, M], [F])
    d = res["details"]
    assert _key(res) == M and d["effective_case"] == 75 and d["answer_borrowed"] is True
    assert "answer_from_other_case" in d["review_flags"]
    assert d["source_case"] == {"case": 75, "wife": [M], "husband": [F, M, F]}
    assert res["outcomes"][0]["probability"] is None


# Borrowed answer from case 72
def test_borrowed_72(s, created):
    res = _post(s, created, [F, M, F], [M])
    d = res["details"]
    assert _key(res) == F and d["effective_case"] == 72 and d["answer_borrowed"] is True


# Not in table
def test_not_in_table(s, created):
    res = _post(s, created, [M, F, F], [M])
    assert res["outcomes"] == [] and res["details"]["review_flags"] == ["not_in_table"]


# Exact split duplicate 41
def test_exact_41(s, created):
    res = _post(s, created, [M, M], [M, M])
    d = res["details"]
    assert _key(res) == M and d["effective_case"] == 41 and d["review_flags"] == ["duplicate_pattern"]
    assert d["answer_borrowed"] is False


# Old app only case 37 localized
@pytest.mark.parametrize("lang", ["en", "ar", "de"])
def test_old_app_only_37(s, created, lang):
    res = _post(s, created, [M], [F], lang=lang)
    d = res["details"]
    assert d["effective_case"] == 37 and d["origin"] == "old_app_only" and "old_app_only" in d["review_flags"]
    for lim in res["limitations"]:
        txt = lim["text"]
        assert txt and txt != lim["key"] and "_" not in txt, lim
    if lang == "ar":
        assert any("التطبيق القديم" in l["text"] for l in res["limitations"])


# Random spot-check of 30 baseline pairs via API
def test_baseline_spot_check(s, created):
    base = json.loads(BASELINE.read_text(encoding="utf-8"))["results"]
    rng = random.Random(7)
    sample = rng.sample(sorted(base), 15)
    bad = []
    for k in sample:
        w, h, n = k.split("|")
        got = _key(_post(s, created, w.split(","), h.split(","), int(n)))
        if got != base[k]:
            bad.append((k, base[k], got))
        time.sleep(2.2)
    assert not bad, bad


# History lists family-pattern
def test_history(s, created):
    items = s.get(f"{API}/analyses?lang=en&limit=200").json()["items"]
    assert any(i.get("analysis_type") == "family-pattern" for i in items)
