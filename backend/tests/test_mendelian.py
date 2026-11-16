"""Textbook Mendelian crosses. Expected values: standard genetics (MedlinePlus inheritance patterns)."""
import pytest

from genova.genetics import GeneticsInputError, mendelian_analysis


def dist(result, kind="phenotype", group="all_children"):
    return {o["key"]: o["fraction"] for o in result["outcomes"] if o["kind"] == kind and o["group"] == group}


def test_monohybrid_heterozygous_cross_1_2_1():
    r = mendelian_analysis("autosomal_recessive", "Aa", "Aa")
    assert dist(r, "genotype") == {"AA": "1/4", "Aa": "1/2", "aa": "1/4"}
    assert dist(r) == {"shows_trait": "1/4", "carrier_no_trait": "1/2", "no_trait_non_carrier": "1/4"}
    assert r["certainty"] == "established"
    assert r["details"]["grid"]["cells"] == [["AA", "Aa"], ["Aa", "aa"]]


def test_dominant_heterozygote_x_homozygous_recessive_is_half():
    r = mendelian_analysis("autosomal_dominant", "Aa", "aa")
    assert dist(r) == {"shows_trait": "1/2", "no_trait": "1/2"}


def test_dominant_homozygote_all_children_show_trait():
    assert dist(mendelian_analysis("autosomal_dominant", "AA", "aa")) == {"shows_trait": "1"}


def test_dominant_heterozygous_cross_three_quarters():
    assert dist(mendelian_analysis("autosomal_dominant", "Aa", "Aa")) == {"shows_trait": "3/4", "no_trait": "1/4"}


def test_recessive_affected_x_carrier():
    r = mendelian_analysis("autosomal_recessive", "aa", "Aa")
    assert dist(r) == {"shows_trait": "1/2", "carrier_no_trait": "1/2"}


def test_genotype_order_is_normalised():
    assert dist(mendelian_analysis("autosomal_recessive", "aA", "Aa"), "genotype") == {"AA": "1/4", "Aa": "1/2", "aa": "1/4"}


def test_codominant_and_incomplete():
    r = mendelian_analysis("codominant", "AB", "AB")
    assert dist(r) == {"allele_A_trait": "1/4", "both_expressed": "1/2", "allele_B_trait": "1/4"}
    r = mendelian_analysis("incomplete_dominance", "AA", "BB")
    assert dist(r) == {"intermediate": "1"}


def test_x_linked_recessive_carrier_mother_unaffected_father():
    r = mendelian_analysis("x_linked_recessive", "XAXa", "XAY")
    assert dist(r, group="sons") == {"shows_trait": "1/2", "no_trait": "1/2"}
    assert dist(r, group="daughters") == {"carrier_no_trait": "1/2", "no_trait_non_carrier": "1/2"}


def test_x_linked_recessive_affected_father_non_carrier_mother():
    r = mendelian_analysis("x_linked_recessive", "XAXA", "XaY")
    assert dist(r, group="sons") == {"no_trait": "1"}
    assert dist(r, group="daughters") == {"carrier_no_trait": "1"}


def test_x_linked_recessive_affected_mother_all_sons_affected():
    r = mendelian_analysis("x_linked_recessive", "XaXa", "XAY")
    assert dist(r, group="sons") == {"shows_trait": "1"}


def test_x_linked_dominant_affected_father_all_daughters_no_sons():
    r = mendelian_analysis("x_linked_dominant", "XaXa", "XAY")
    assert dist(r, group="daughters") == {"shows_trait": "1"}
    assert dist(r, group="sons") == {"no_trait": "1"}


@pytest.mark.parametrize("mode,p1,p2", [
    ("autosomal_recessive", "AB", "Aa"), ("codominant", "Aa", "AB"), ("x_linked_recessive", "XAY", "XAY"),
    ("x_linked_recessive", "XAXa", "XAXa"), ("autosomal_dominant", "A", "Aa"), ("bogus", "Aa", "Aa"),
])
def test_invalid_inputs_rejected(mode, p1, p2):
    with pytest.raises(GeneticsInputError):
        mendelian_analysis(mode, p1, p2)
