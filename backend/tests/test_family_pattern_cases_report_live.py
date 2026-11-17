"""Live API tests: PDF cases 61-68/81-91, single-child scope, child_number rules, baseline sample (iteration 8)."""
import json
import os
import subprocess
import time
from pathlib import Path

import pytest
import requests
from dotenv import dotenv_values
from live_roles import as_role

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
    with as_role(sess, API, "admin"):  # admin sees the protected details these tests check
        yield sess
    for i in created:
        sess.delete(f"{API}/analyses/{i}")


def _raw(s, body, lang="en"):
    for _ in range(6):
        r = s.post(f"{API}/analyses/family-pattern?lang={lang}", json=body)
        if r.status_code != 429:
            return r
        time.sleep(15)
    return r


def _post(s, created, wife, husband, n=None, lang="en"):
    body = {"wife": wife, "husband": husband, **({"child_number": n} if n else {})}
    r = _raw(s, body, lang)
    assert r.status_code == 200, r.text
    d = r.json()
    created.add(d["id"])
    return d


def _key(res):
    return res["outcomes"][0]["key"] if res["outcomes"] else None


# New PDF cases 61, 81, 91 are their own entries
@pytest.mark.parametrize("wife,husband,case,ans",
                         [([F, F], [F], 61, F), ([F, F, F], [F], 81, F), ([F, M, M], [M], 91, M)])
def test_new_pdf_cases(s, created, wife, husband, case, ans):
    res = _post(s, created, wife, husband)["result"]
    d = res["details"]
    assert d["effective_case"] == case and d["origin"] == "original_pdf" and d["answer_borrowed"] is False
    assert res["outcomes"][0]["group"] == "single_child" and _key(res) == ans
    assert res["outcomes"][0]["group_label"] == "Baby" and res["outcomes"][0]["probability"] is None


# Pending cases 84/87/92 keep today's answers
def test_pending_cases_unchanged(s, created):
    r84 = _post(s, created, [M, F, M], [F])["result"]
    assert _key(r84) == M and r84["details"]["effective_case"] == 75 and r84["details"]["answer_borrowed"] is True
    r87 = _post(s, created, [F, M, F], [M])["result"]
    assert _key(r87) == F and r87["details"]["effective_case"] == 72 and r87["details"]["answer_borrowed"] is True
    r92 = _post(s, created, [M, F, F], [M])["result"]
    assert r92["outcomes"] == [] and "not_in_table" in r92["details"]["review_flags"]


# 3+3 requires child_number (localized 400)
@pytest.mark.parametrize("lang,frag", [("en", "first or second"), ("ar", "الطفل الأول"), ("de", "erste oder zweite")])
def test_three_three_requires_child(s, lang, frag):
    r = _raw(s, {"wife": [M, M, F], "husband": [M, M, F]}, lang)
    assert r.status_code == 400, r.text
    det = r.json()["detail"]
    assert det["code"] == "child_number_required" and frag in det["message"]


# 3+3 with child 1/2 gives first_child/second_child
def test_three_three_groups(s, created):
    a = _post(s, created, [M, M, F], [M, M, F], 1)["result"]
    b = _post(s, created, [M, M, F], [M, M, F], 2)["result"]
    assert a["outcomes"][0]["group"] == "first_child" and b["outcomes"][0]["group"] == "second_child"
    assert a["inputs"]["child_number"] == 1 and b["inputs"]["child_number"] == 2


# Non-3+3 with child_number 1/2 -> same result, child_number null, deduped
def test_non33_child_number_ignored_and_deduped(s, created):
    a = _post(s, created, [M, F], [M, M], 1)
    b = _post(s, created, [M, F], [M, M], 2)
    c = _post(s, created, [M, F], [M, M])
    assert a["id"] == b["id"] == c["id"]
    assert a["request"]["child_number"] is None and a["result"]["inputs"]["child_number"] is None
    assert _key(a["result"]) == _key(b["result"])


# Single-child label localized
@pytest.mark.parametrize("lang,label", [("ar", "طفل"), ("de", "Kind")])
def test_single_label_localized(s, created, lang, label):
    res = _post(s, created, [M], [F], lang=lang)["result"]
    assert res["outcomes"][0]["group_label"] == label and "old_app_only" in res["details"]["review_flags"]
    assert res["details"]["effective_case"] == 37


def _sample_mismatch(s, created, base, index, pair):
    w, h = (part.split(",") for part in pair.split("|"))
    n = index % 2 + 1 if len(w) == 3 and len(h) == 3 else None
    got = _key(_post(s, created, w, h, n)["result"])
    exp = base[f"{pair}|{n or 1}"]
    return None if got == exp else (pair, n, exp, got)


# Deterministic baseline sample through the API: 30 evenly spaced pairs, alternating child 1/2 for 3+3
def test_baseline_sample(s, created):
    base = json.loads(BASELINE.read_text())["results"]
    keys = sorted({k.rsplit("|", 1)[0] for k in base})
    bad = []
    for i, pair in enumerate(keys[:: len(keys) // 30][:30]):
        bad.append(_sample_mismatch(s, created, base, i, pair))
        time.sleep(1.5)
    assert not any(bad), [b for b in bad if b]
