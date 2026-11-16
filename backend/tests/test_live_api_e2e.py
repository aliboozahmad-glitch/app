"""Live end-to-end API tests against the public preview URL with real Clerk tokens.
Tokens come from /app/scripts/clerk_test_session.py (run at module setup)."""
import json
import os
import subprocess
from pathlib import Path

import pytest
import requests
from dotenv import dotenv_values

BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL")
            or dotenv_values(Path("/app/frontend/.env"))["REACT_APP_BACKEND_URL"]).rstrip("/")
API = f"{BASE_URL}/api"
USER_A = "genova.tester+clerk_test@example.com"
USER_B = "genova.other+clerk_test@example.com"


def _session(email):
    out = subprocess.run(["python", "/app/scripts/clerk_test_session.py", email], capture_output=True, text=True,
                         timeout=60)
    if out.returncode != 0:
        pytest.skip(f"clerk session failed: {out.stderr[-300:]}")
    return json.loads(out.stdout)["token"]


@pytest.fixture(scope="module")
def created():
    return []


@pytest.fixture(scope="module")
def a(created):
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {_session(USER_A)}"
    yield s
    for i in created:
        s.delete(f"{API}/analyses/{i}")


@pytest.fixture(scope="module")
def b():
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {_session(USER_B)}"
    return s


def post(s, kind, body, created, lang="en"):
    r = s.post(f"{API}/analyses/{kind}?lang={lang}", json=body)
    if r.status_code == 200:
        created.append(r.json()["id"])
    return r


def by(outcomes, key, group=None, kind=None):
    return next(o for o in outcomes if o["key"] == key and (group is None or o["group"] == group)
            and (kind is None or o["kind"] == kind))


# --- Public endpoints
def test_public_endpoints():
    assert requests.get(f"{API}/health").json()["status"] == "ok"
    for lang in ("ar", "en", "de"):
        c = requests.get(f"{API}/catalog?lang={lang}").json()
        ids = {d["id"] for d in c["diseases"]}
        assert len(ids) == 10 and {"g6pd_deficiency", "beta_thalassemia"} <= ids
    refs = requests.get(f"{API}/references").json()["references"]
    assert len(refs) > 0


# --- Auth required
@pytest.mark.parametrize("method,path", [("get", "/me"), ("get", "/analyses"), ("post", "/analyses/mendelian")])
def test_protected_401(method, path):
    r = getattr(requests, method)(f"{API}{path}", json={"mode": "autosomal_recessive", "parent1": "Aa",
                                                        "parent2": "Aa"})
    assert r.status_code == 401


def test_me(a):
    r = a.get(f"{API}/me")
    assert r.status_code == 200 and r.json()["role"] == "member" and r.json()["email"] == USER_A


# --- Scientific correctness via live API
def test_ar_cross(a, created):
    r = post(a, "mendelian", {"mode": "autosomal_recessive", "parent1": "Aa", "parent2": "Aa"}, created)
    res = r.json()["result"]
    assert res["certainty"] == "established" and res["method_label"]
    assert by(res["outcomes"], "shows_trait")["fraction"] == "1/4"
    assert by(res["outcomes"], "carrier_no_trait")["fraction"] == "1/2"
    assert by(res["outcomes"], "no_trait_non_carrier")["fraction"] == "1/4"
    assert res["limitations"][0]["key"] == "not_diagnosis"
    assert res["assumptions"] and res["references"]


def test_xr_cross(a, created):
    res = post(a, "mendelian", {"mode": "x_linked_recessive", "parent1": "XAXa", "parent2": "XAY"},
               created).json()["result"]
    assert by(res["outcomes"], "shows_trait", "sons", "phenotype")["fraction"] == "1/2"
    assert by(res["outcomes"], "carrier_no_trait", "daughters", "phenotype")["fraction"] == "1/2"


def test_blood_ab_o(a, created):
    res = post(a, "blood-type", {"parent1_abo": "AB", "parent1_rh": "+", "parent2_abo": "O", "parent2_rh": "-"},
               created).json()["result"]
    abo = {o["key"]: o for o in res["outcomes"]}
    print(json.dumps(res["details"])[:600])
    assert "O+" not in abo and "O-" not in abo and "O" not in abo
    assert "O" in json.dumps(res["details"].get("impossible", res["details"]))


def test_blood_a_b_ranges(a, created):
    res = post(a, "blood-type", {"parent1_abo": "A", "parent1_rh": "+", "parent2_abo": "B", "parent2_rh": "+"},
               created).json()["result"]
    assert all(o["fraction"] is None and o.get("range") for o in res["outcomes"])


def test_height(a, created):
    res = post(a, "height", {"mother_cm": 165, "father_cm": 180}, created).json()["result"]
    sons = next(o for o in res["outcomes"] if o["group"] == "sons")
    daughters = next(o for o in res["outcomes"] if o["group"] == "daughters")
    assert sons["value"] == 179 and sons["range"] == [170.5, 187.5] and daughters["value"] == 166
    assert res["certainty"] == "statistical_estimate"


def test_sex_ratio(a, created):
    res = post(a, "sex-ratio", {}, created).json()["result"]
    assert any(o.get("fraction") == "21/41" for o in res["outcomes"])


def test_pigmentation(a, created):
    res = post(a, "pigmentation", {"trait": "eye_color", "mother": "blue", "father": "brown"},
               created).json()["result"]
    assert res["certainty"] == "uncertain_estimate" and all(o["probability"] is None for o in res["outcomes"])


def test_g6pd(a, created):
    res = post(a, "carrier-risk", {"disease_id": "g6pd_deficiency", "mother_status": "carrier",
                                   "father_status": "unaffected"}, created).json()["result"]
    assert by(res["outcomes"], "heterozygous_variable", "daughters")["fraction"] == "1/2"


def test_beta_thal_unknown(a, created):
    res = post(a, "carrier-risk", {"disease_id": "beta_thalassemia", "mother_status": "carrier",
                                   "father_status": "unknown", "region": "gulf"}, created, "ar").json()["result"]
    assert res["method"] == "carrier_conditional" and res["outcomes"] == []
    assert res["details"]["scenarios"] and res["details"]["population_estimate"]["available"] is False
    assert res["lang"] == "ar"


# --- Validation
def test_invalid_genotype_localized(a):
    en = a.post(f"{API}/analyses/mendelian?lang=en", json={"mode": "autosomal_recessive", "parent1": "Zz",
                                                           "parent2": "Aa"})
    de = a.post(f"{API}/analyses/mendelian?lang=de", json={"mode": "autosomal_recessive", "parent1": "Zz",
                                                           "parent2": "Aa"})
    assert en.status_code == 400 and en.json()["detail"]["code"] == "invalid_genotype"
    assert en.json()["detail"]["message"] != de.json()["detail"]["message"]


def test_422s_and_404(a):
    assert a.post(f"{API}/analyses/height", json={"mother_cm": 50, "father_cm": 180}).status_code == 422
    assert a.post(f"{API}/analyses/height", json={"mother_cm": 165, "father_cm": 180, "x": 1}).status_code == 422
    assert a.get(f"{API}/analyses/notanid").status_code == 404
    assert a.post(f"{API}/analyses/unknown-kind", json={}).status_code == 404


# --- Persistence, relocalize, isolation, delete
def test_persist_isolation_delete(a, b, created):
    r = post(a, "mendelian", {"mode": "autosomal_dominant", "parent1": "Aa", "parent2": "aa"}, created)
    aid = r.json()["id"]
    g = a.get(f"{API}/analyses/{aid}?lang=de").json()
    assert g["result"]["lang"] == "de" and g["result"]["method_label"] != r.json()["result"]["method_label"]
    assert any(i["id"] == aid for i in a.get(f"{API}/analyses").json()["items"])
    assert b.get(f"{API}/analyses/{aid}").status_code == 404
    assert b.delete(f"{API}/analyses/{aid}").status_code == 404
    assert all(i["id"] != aid for i in b.get(f"{API}/analyses").json()["items"])
    assert b.get(f"{API}/users").status_code == 403
    assert a.delete(f"{API}/analyses/{aid}").status_code == 200
    assert a.get(f"{API}/analyses/{aid}").status_code == 404
