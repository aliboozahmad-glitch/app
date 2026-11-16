"""Owner's traditional family-pattern table (from the legacy app), reproduced exactly.

Not a scientific method and not part of genova.genetics. No randomness, no confidence scores.
Original lookup is preserved: key = wife's children + husband's children; a repeated key uses the
later entry. Anything not confirmed by the owner is flagged, never silently corrected.
"""
import json
from functools import lru_cache
from pathlib import Path

from ..genetics.core import GeneticsInputError

GENDERS = ("male", "female")
UNCONFIRMED_SECTIONS = {"one_plus_two", "one_plus_three"}
DATA = Path(__file__).parent / "data" / "family_pattern_table.json"


@lru_cache(maxsize=1)
def load_table() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def _validate(wife: list, husband: list, child_number: int) -> None:
    for family in (wife, husband):
        if not 1 <= len(family) <= 3 or any(g not in GENDERS for g in family):
            raise GeneticsInputError("invalid_family_pattern")
    if child_number not in (1, 2):
        raise GeneticsInputError("invalid_child_number")


def _review_flags(matches: list, effective: dict, wife: list, husband: list) -> list:
    flags = []
    if len(matches) > 1:
        flags.append("duplicate_pattern")
    if effective["section"] in UNCONFIRMED_SECTIONS:
        flags.append("split_unconfirmed")
    elif [len(effective["wife"]), len(effective["husband"])] != [len(wife), len(husband)]:
        flags.append("split_mismatch")
    return flags


def family_pattern_analysis(wife: list, husband: list, child_number: int) -> dict:
    _validate(wife, husband, child_number)
    table = load_table()
    key = [*wife, *husband]
    matches = [c for c in table["cases"] if c["pattern"] == key]
    group = "first_child" if child_number == 1 else "second_child"
    details = {"matched_cases": [c["case"] for c in matches], "entered_split": [len(wife), len(husband)],
               "review_status": table["review_status"], "statistic_separate": True}
    limitations = ["traditional_not_scientific", "no_confidence_score"]
    outcomes = []
    if matches:
        effective = matches[-1]  # original dict behaviour: later definition wins
        details |= {"effective_case": effective["case"], "section": effective["section"]}
        flags = _review_flags(matches, effective, wife, husband)
        details["review_flags"] = flags
        limitations += flags
        prediction = effective["result"]["first" if child_number == 1 else "second"]
        outcomes.append({"key": prediction, "kind": "traditional", "group": group, "probability": None,
                         "fraction": None})
    else:
        details |= {"review_flags": ["not_in_table"], "original_fallback": "male"}
        limitations.append("not_in_table")
    return {
        "analysis_type": "family_pattern",
        "certainty": "traditional_belief",
        "method": "family_pattern_table",
        "inputs": {"wife": wife, "husband": husband, "child_number": child_number},
        "outcomes": outcomes,
        "assumptions": ["traditional_table_as_provided"],
        "limitations": ["not_diagnosis", *limitations],
        "references": ["legacy-family-pattern-table"],
        "details": details,
        "engine_version": "genova-traditional 1.0.0",
        "data_version": table["version"],
    }
