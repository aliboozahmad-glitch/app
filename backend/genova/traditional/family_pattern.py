"""Owner's traditional family-pattern table (from the legacy app), reproduced exactly.

Not a scientific method and not part of genova.genetics. No randomness, no confidence scores.
Wife's and husband's families are stored separately. Until the owner approves individual cases, every
answer is the old app's answer: an exact wife/husband entry if one exists, else the old joined-list
lookup (later entry wins), with the source case shown. Cases 30-40 are archived as "old app only".
"""
import json
from functools import lru_cache
from pathlib import Path

from ..genetics.core import GeneticsInputError

GENDERS = ("male", "female")
DATA = Path(__file__).parent / "data" / "family_pattern_table.json"


@lru_cache(maxsize=1)
def load_table() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def legacy_order() -> list:
    t = load_table()
    return sorted([*t["cases"], *t["old_app_only_cases"]], key=lambda c: c["source_line"])


def _validate(wife: list, husband: list, child_number: int) -> None:
    for family in (wife, husband):
        if not 1 <= len(family) <= 3 or any(g not in GENDERS for g in family):
            raise GeneticsInputError("invalid_family_pattern")
    if child_number not in (1, 2):
        raise GeneticsInputError("invalid_child_number")


def _pick(wife: list, husband: list) -> tuple:
    joined = [c for c in legacy_order() if c["pattern"] == [*wife, *husband]]
    exact = [c for c in joined if c["wife"] == wife and c["husband"] == husband]
    if exact:
        return joined, exact[-1], False
    return joined, (joined[-1] if joined else None), bool(joined)


def _flags(joined: list, effective: dict, borrowed: bool) -> list:
    flags = ["duplicate_pattern"] if len(joined) > 1 else []
    if borrowed:
        flags.append("answer_from_other_case")
    if effective["origin"] == "old_app_only":
        flags.append("old_app_only")
    return flags


def family_pattern_analysis(wife: list, husband: list, child_number: int) -> dict:
    _validate(wife, husband, child_number)
    table = load_table()
    joined, effective, borrowed = _pick(wife, husband)
    group = "first_child" if child_number == 1 else "second_child"
    details = {"matched_cases": [c["case"] for c in joined], "entered_split": [len(wife), len(husband)],
               "review_status": table["review_status"], "statistic_separate": True}
    limitations = ["traditional_not_scientific", "no_confidence_score"]
    outcomes = []
    if effective:
        flags = _flags(joined, effective, borrowed)
        details |= {"effective_case": effective["case"], "section": effective["section"],
                    "origin": effective["origin"], "answer_borrowed": borrowed, "review_flags": flags,
                    "source_case": {"case": effective["case"], "wife": effective["wife"],
                                    "husband": effective["husband"]}}
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
        "engine_version": "genova-traditional 1.1.0",
        "data_version": table["version"],
    }
