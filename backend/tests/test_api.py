"""API integration tests against the real app and local MongoDB. Auth is overridden with test members."""
import pytest
from fastapi.testclient import TestClient

from genova.auth import current_member
from server import app

USER_A = {"user_id": "test_user_a", "role": "member", "env": "preview"}
USER_B = {"user_id": "test_user_b", "role": "member", "env": "preview"}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def as_user(user):
    app.dependency_overrides[current_member] = lambda: user


@pytest.fixture(autouse=True)
def cleanup(client):
    yield
    app.dependency_overrides.clear()


def test_health_and_public_catalog(client):
    assert client.get("/api/health").json()["status"] == "ok"
    cat = client.get("/api/catalog?lang=ar").json()
    assert len(cat["diseases"]) == 10
    assert any(d["id"] == "g6pd_deficiency" for d in cat["diseases"])
    assert client.get("/api/references").json()["references"]


def test_protected_routes_require_auth(client):
    assert client.post("/api/analyses/mendelian", json={"mode": "autosomal_recessive", "parent1": "Aa",
                                                        "parent2": "Aa"}).status_code in (401, 503)
    assert client.get("/api/analyses").status_code in (401, 503)
    assert client.get("/api/me").status_code in (401, 503)


def test_member_cannot_access_admin(client):
    as_user(USER_A)
    assert client.get("/api/users").status_code == 403


def test_analysis_roundtrip_localised_and_isolated(client):
    as_user(USER_A)
    r = client.post("/api/analyses/carrier-risk?lang=de",
                    json={"disease_id": "beta_thalassemia", "mother_status": "carrier", "father_status": "carrier"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["result"]["certainty_label"] == "Gesichert (Mendelsch)"
    aid = body["id"]
    ar = client.get(f"/api/analyses/{aid}?lang=ar").json()
    assert ar["result"]["details"]["disease_name"] == "الثلاسيميا بيتا"
    assert any(i["id"] == aid for i in client.get("/api/analyses").json()["items"])

    as_user(USER_B)
    assert client.get(f"/api/analyses/{aid}").status_code == 404
    assert client.delete(f"/api/analyses/{aid}").status_code == 404
    assert all(i["id"] != aid for i in client.get("/api/analyses").json()["items"])

    as_user(USER_A)
    assert client.delete(f"/api/analyses/{aid}").status_code == 200


@pytest.mark.parametrize("kind,body", [
    ("mendelian", {"mode": "x_linked_recessive", "parent1": "XAXa", "parent2": "XAY"}),
    ("blood-type", {"parent1_abo": "A", "parent1_rh": "+", "parent2_abo": "O", "parent2_rh": "-"}),
    ("height", {"mother_cm": 162, "father_cm": 178}),
    ("pigmentation", {"trait": "eye_color", "mother": "brown", "father": "blue"}),
    ("sex-ratio", {}),
])
def test_all_calculators(client, kind, body):
    as_user(USER_A)
    r = client.post(f"/api/analyses/{kind}?lang=en", json=body)
    assert r.status_code == 200, r.text
    res = r.json()["result"]
    assert res["references"] and res["limitations"][0]["key"] == "not_diagnosis"
    client.delete(f"/api/analyses/{r.json()['id']}")


def test_validation_errors(client):
    as_user(USER_A)
    r = client.post("/api/analyses/height", json={"mother_cm": 50, "father_cm": 170})
    assert r.status_code == 422 and r.json()["detail"]["code"] == "validation_error"
    r = client.post("/api/analyses/mendelian", json={"mode": "x_linked_recessive", "parent1": "Aa", "parent2": "XAY"})
    assert r.status_code == 400 and r.json()["detail"]["code"] == "invalid_genotype"
    r = client.post("/api/analyses/mendelian?lang=ar", json={"mode": "autosomal_recessive", "parent1": "Aa",
                                                              "parent2": "Aa", "role": "admin"})
    assert r.status_code == 422  # extra fields rejected
    assert client.post("/api/analyses/unknown", json={}).status_code == 404
    assert client.get("/api/analyses/not-an-id").status_code == 404
