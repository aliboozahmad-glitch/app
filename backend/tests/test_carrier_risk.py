import copy

import pytest

from genova.genetics import GeneticsInputError, carrier_analysis
from genova.genetics.data_loader import load_diseases


def d(r, group="all_children"):
    return {o["key"]: o["fraction"] for o in r["outcomes"] if o["group"] == group}


def test_two_confirmed_carriers_ar():
    r = carrier_analysis("beta_thalassemia", "carrier", "carrier")
    assert r["certainty"] == "established"
    assert d(r) == {"affected": "1/4", "carrier": "1/2", "unaffected_non_carrier": "1/4"}


def test_carrier_x_non_carrier_ar_no_affected_but_residual_warning():
    r = carrier_analysis("cystic_fibrosis", "carrier", "non_carrier")
    assert d(r) == {"carrier": "1/2", "unaffected_non_carrier": "1/2"}
    assert "negative_test_residual" in r["limitations"]


def test_affected_x_carrier_ar():
    assert d(carrier_analysis("sickle_cell", "affected", "carrier")) == {"affected": "1/2", "carrier": "1/2"}


def test_hemophilia_carrier_mother():
    r = carrier_analysis("hemophilia_a", "carrier", "unaffected")
    assert d(r, "sons") == {"affected": "1/2", "unaffected": "1/2"}
    assert d(r, "daughters") == {"carrier": "1/2", "unaffected_non_carrier": "1/2"}
    assert "de_novo_possible" in r["limitations"]


def test_g6pd_daughters_reported_as_variable_not_carrier():
    r = carrier_analysis("g6pd_deficiency", "carrier", "unaffected")
    assert d(r, "daughters") == {"heterozygous_variable": "1/2", "unaffected_non_carrier": "1/2"}
    assert "g6pd_female_variable" in r["limitations"]


def test_g6pd_affected_father_all_daughters_heterozygous():
    r = carrier_analysis("g6pd_deficiency", "non_carrier", "affected")
    assert d(r, "daughters") == {"heterozygous_variable": "1"}
    assert d(r, "sons") == {"unaffected": "1"}


def test_unknown_status_without_validated_data_gives_scenarios_only():
    r = carrier_analysis("beta_thalassemia", "carrier", "unknown", "gulf")
    assert r["method"] == "carrier_conditional"
    assert r["outcomes"] == []
    assert r["details"]["population_estimate"] == {"available": False, "reason": "region_data_unvalidated"}
    scen = {s["father_genotype"]: {o["key"]: o["fraction"] for o in s["outcomes"]} for s in r["details"]["scenarios"]}
    assert scen["Aa"]["affected"] == "1/4"
    assert "affected" not in scen["AA"]


def test_population_estimate_uses_only_validated_data():
    data = copy.deepcopy(load_diseases())
    data["cystic_fibrosis"]["regional"] = [
        {"region": "europe", "status": "validated", "carrier_frequency": "1/25", "source": "who-cf-2004",
         "reviewed_by": "test-fixture"}]
    r = carrier_analysis("cystic_fibrosis", "carrier", "unknown", "europe", diseases=data)
    assert r["certainty"] == "population_estimate"
    assert d(r)["affected"] == "1/100"  # 1/25 * 1/4
    r2 = carrier_analysis("cystic_fibrosis", "unknown", "unknown", "europe", diseases=data)
    assert d(r2)["affected"] == "1/2500"  # 1/25 * 1/25 * 1/4


def test_x_linked_population_estimate_father_unknown():
    data = copy.deepcopy(load_diseases())
    data["hemophilia_a"]["regional"] = [
        {"region": "global", "status": "validated", "carrier_frequency": "1/5000", "affected_male_frequency": "1/5000",
         "source": "mlp-hemophilia", "reviewed_by": "test-fixture"}]
    r = carrier_analysis("hemophilia_a", "non_carrier", "unknown", "global", diseases=data)
    assert d(r, "daughters")["carrier"] == "1/5000"


def test_draft_data_never_used():
    for disease_id in [k for k in load_diseases() if not k.startswith("_")]:
        r = carrier_analysis(disease_id, "unknown", "unknown", "global")
        assert r["certainty"] == "established" and r["outcomes"] == []


@pytest.mark.parametrize("disease,m,f", [("nope", "carrier", "carrier"), ("hemophilia_a", "carrier", "carrier"),
                                         ("beta_thalassemia", "carrier", "unaffected")])
def test_invalid(disease, m, f):
    with pytest.raises(GeneticsInputError):
        carrier_analysis(disease, m, f)
