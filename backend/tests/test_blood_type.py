import pytest

from genova.genetics import GeneticsInputError, blood_type_analysis


def exact(r):
    return {o["key"]: o["fraction"] for o in r["outcomes"]}


def test_ab_x_o_gives_only_a_or_b():
    r = blood_type_analysis("AB", "dd", "O", "dd")
    assert exact(r) == {"A-": "1/2", "B-": "1/2"}
    assert r["details"]["exact"] is True
    assert "O-" in r["details"]["impossible_types"] and "AB-" in r["details"]["impossible_types"]


def test_o_x_o_only_o():
    r = blood_type_analysis("O", "-", "O", "-")
    assert exact(r) == {"O-": "1"}


def test_ao_x_bo_all_four_quarter_each_abo():
    r = blood_type_analysis("AO", "dd", "BO", "dd")
    assert exact(r) == {"A-": "1/4", "B-": "1/4", "AB-": "1/4", "O-": "1/4"}


def test_rh_heterozygotes_three_quarters_positive():
    r = blood_type_analysis("OO", "Dd", "OO", "Dd")
    assert exact(r) == {"O+": "3/4", "O-": "1/4"}


def test_rh_negative_parents_cannot_have_positive_child():
    r = blood_type_analysis("A", "-", "B", "-")
    assert all(t.endswith("-") for t in r["details"]["possible_types"])


def test_phenotype_only_gives_ranges_not_single_numbers():
    r = blood_type_analysis("A", "+", "B", "+")
    assert r["details"]["exact"] is False
    ab_pos = next(o for o in r["outcomes"] if o["key"] == "AB+")
    assert ab_pos["probability"] is None
    assert ab_pos["range_fraction"] == ["3/16", "1"]
    assert r["details"]["possible_types"] == ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]


def test_a_x_a_cannot_have_b_or_ab():
    r = blood_type_analysis("A", "+", "A", "+")
    assert set(r["details"]["impossible_types"]) == {"B+", "B-", "AB+", "AB-"}


@pytest.mark.parametrize("abo,rh", [("C", "+"), ("A", "x"), ("AX", "+"), ("A", "DX")])
def test_invalid(abo, rh):
    with pytest.raises(GeneticsInputError):
        blood_type_analysis(abo, rh, "O", "+")
