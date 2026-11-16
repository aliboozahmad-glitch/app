"""Polygenic traits. Height: Tanner mid-parental target height. Pigmentation: qualitative only, no percentages."""
from decimal import ROUND_HALF_UP, Decimal

from .core import GeneticsInputError, make_result

TANNER_SEX_OFFSET_CM = Decimal("13")
TANNER_RANGE_CM = Decimal("8.5")
MIN_CM, MAX_CM = 120, 230

EYE = ("brown", "hazel", "green", "blue", "gray")
HAIR = ("black", "brown", "blonde", "red")
LIGHT_EYES = {"blue", "gray"}


def _r(x: Decimal) -> float:
    return float(x.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def height_analysis(mother_cm, father_cm) -> dict:
    m, f = Decimal(str(mother_cm)), Decimal(str(father_cm))
    if not (MIN_CM <= m <= MAX_CM and MIN_CM <= f <= MAX_CM):
        raise GeneticsInputError("height_out_of_range")
    outcomes = []
    for group, sign in (("sons", 1), ("daughters", -1)):
        target = (m + f + sign * TANNER_SEX_OFFSET_CM) / 2
        outcomes.append({"key": "target_height_cm", "kind": "measurement", "group": group, "value": _r(target),
                         "range": [_r(target - TANNER_RANGE_CM), _r(target + TANNER_RANGE_CM)], "unit": "cm"})
    return make_result("height", "statistical_estimate", "mid_parental_height",
                       {"mother_cm": float(m), "father_cm": float(f)}, outcomes,
                       ["adult_height_both_parents", "typical_growth"], ["height_environment", "height_range_approx"],
                       ["tanner-1970", "medlineplus-height"],
                       {"formula": {"sons": "(mother + father + 13) / 2", "daughters": "(mother + father - 13) / 2",
                                    "range_cm": float(TANNER_RANGE_CM)}})


def _eye_bands(m, f):
    both_light = m in LIGHT_EYES and f in LIGHT_EYES
    any_brown = "brown" in (m, f)
    if both_light:
        return {"more_often_observed": ["blue", "gray"], "possible": ["green", "hazel"], "less_common": ["brown"]}
    if any_brown:
        rest = [c for c in EYE if c != "brown"]
        return {"more_often_observed": ["brown"], "possible": rest, "less_common": []}
    common = sorted({m, f}, key=EYE.index)
    return {"more_often_observed": common, "possible": [c for c in EYE if c not in common], "less_common": []}


def _hair_bands(m, f):
    if m == f == "red":
        return {"more_often_observed": ["red"], "possible": ["blonde", "brown"], "less_common": ["black"]}
    if m == f == "blonde":
        return {"more_often_observed": ["blonde"], "possible": ["brown", "red"], "less_common": ["black"]}
    dark = [c for c in ("black", "brown") if c in (m, f)]
    if dark:
        return {"more_often_observed": dark, "possible": [c for c in HAIR if c not in dark], "less_common": []}
    common = sorted({m, f}, key=HAIR.index)
    return {"more_often_observed": common, "possible": [c for c in HAIR if c not in common], "less_common": []}


def pigmentation_analysis(trait: str, mother: str, father: str) -> dict:
    table = {"eye_color": (EYE, _eye_bands, "medlineplus-eye-color"),
             "hair_color": (HAIR, _hair_bands, "medlineplus-hair-color")}
    if trait not in table:
        raise GeneticsInputError("invalid_trait")
    allowed, fn, ref = table[trait]
    if mother not in allowed or father not in allowed:
        raise GeneticsInputError("invalid_trait_value")
    bands = fn(mother, father)
    outcomes = [{"key": c, "kind": "qualitative", "group": band, "probability": None, "fraction": None}
                for band, colours in bands.items() for c in colours]
    return make_result("pigmentation", "uncertain_estimate", "qualitative_pigmentation",
                       {"trait": trait, "mother": mother, "father": father}, outcomes,
                       ["polygenic_model"], ["polygenic_no_precise", "any_outcome_possible"], [ref],
                       {"bands": bands})
