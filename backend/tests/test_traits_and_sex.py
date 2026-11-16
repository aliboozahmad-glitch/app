import pytest

from genova.genetics import GeneticsInputError, height_analysis, pigmentation_analysis, sex_ratio_analysis


def test_tanner_mid_parental_height():
    r = height_analysis(165, 180)
    sons, daughters = r["outcomes"]
    assert sons["value"] == 179.0 and sons["range"] == [170.5, 187.5]
    assert daughters["value"] == 166.0 and daughters["range"] == [157.5, 174.5]
    assert r["certainty"] == "statistical_estimate"


def test_height_rounding_half_up():
    assert height_analysis(160.5, 170)["outcomes"][0]["value"] == 171.8  # (330.5+13)/2 = 171.75


@pytest.mark.parametrize("m,f", [(100, 170), (170, 260)])
def test_height_range_validation(m, f):
    with pytest.raises(GeneticsInputError):
        height_analysis(m, f)


def test_sex_ratio_105_to_100_not_family_pattern():
    r = sex_ratio_analysis()
    assert {o["key"]: o["fraction"] for o in r["outcomes"]} == {"male": "21/41", "female": "20/41"}
    assert r["certainty"] == "population_statistic"
    assert "family_pattern_not_predictive" in r["limitations"]


def test_pigmentation_has_no_percentages():
    r = pigmentation_analysis("eye_color", "blue", "blue")
    assert r["certainty"] == "uncertain_estimate"
    assert all(o["probability"] is None for o in r["outcomes"])
    assert "brown" in r["details"]["bands"]["less_common"]  # blue x blue can still have brown (MedlinePlus)


def test_every_colour_always_listed():
    for m in ("brown", "blue", "green"):
        for f in ("hazel", "gray", "brown"):
            keys = {o["key"] for o in pigmentation_analysis("eye_color", m, f)["outcomes"]}
            assert keys == {"brown", "hazel", "green", "blue", "gray"}


def test_hair_two_red_parents():
    assert pigmentation_analysis("hair_color", "red", "red")["details"]["bands"]["more_often_observed"] == ["red"]


def test_pigmentation_invalid():
    with pytest.raises(GeneticsInputError):
        pigmentation_analysis("eye_color", "purple", "blue")
