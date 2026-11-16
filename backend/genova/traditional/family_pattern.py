"""Owner's traditional family-pattern table (from the legacy app and the original PDF), reproduced exactly.

Not a scientific method and not part of genova.genetics. No randomness, no confidence scores.
Wife's and husband's families are stored separately. An exact wife/husband entry is used first; otherwise
the old app's joined-list lookup (later entry wins) over old-app entries, with the source case shown.
Only Section 1 (3 + 3 children) predicts a first and second child; all other combinations predict one child.
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


def all_entries() -> list:
    t = load_table()
    return [*t["cases"], *t["old_app_only_cases"]]


def legacy_order() -> list:
    return sorted([c for c in all_entries() if "source_line" in c], key=lambda c: c["source_line"])


def is_two_child_section(wife: list, husband: list) -> bool:
    return len(wife) == 3 and len(husband) == 3


def _validate(wife: list, husband: list, child_number: int | None) -> None:
    for family in (wife, husband):
        if not 1 <= len(family) <= 3 or any(g not in GENDERS for g in family):
            raise GeneticsInputError("invalid_family_pattern")
    if is_two_child_section(wife, husband) and child_number not in (1, 2):
        raise GeneticsInputError("child_number_required")


def _pick(wife: list, husband: list) -> tuple:
    key = [*wife, *husband]
    joined = [c for c in all_entries() if c["pattern"] == key]
    exact = [c for c in joined if c["wife"] == wife and c["husband"] == husband]
    if exact:
        return joined, exact[-1], False
    legacy = [c for c in legacy_order() if c["pattern"] == key]
    return joined, (legacy[-1] if legacy else None), bool(legacy)


def _flags(joined: list, effective: dict, borrowed: bool) -> list:
    flags = ["duplicate_pattern"] if len(joined) > 1 else []
    if borrowed:
        flags.append("answer_from_other_case")
    if effective["origin"] == "old_app_only":
        flags.append("old_app_only")
    return flags


def _outcome(effective: dict, two_child: bool, child_number: int | None) -> dict:
    slot = "second" if two_child and child_number == 2 else "first"
    group = ("first_child" if slot == "first" else "second_child") if two_child else "single_child"
    return {"key": effective["result"][slot], "kind": "traditional", "group": group, "probability": None,
            "fraction": None}


def family_pattern_analysis(wife: list, husband: list, child_number: int | None = None) -> dict:
    _validate(wife, husband, child_number)
    two_child = is_two_child_section(wife, husband)
    child_number = child_number if two_child else None
    table = load_table()
    joined, effective, borrowed = _pick(wife, husband)
    details = {"matched_cases": [c["case"] for c in joined], "entered_split": [len(wife), len(husband)],
               "prediction_scope": "first_and_second_child" if two_child else "single_child",
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
        outcomes.append(_outcome(effective, two_child, child_number))
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
        "engine_version": "genova-traditional 1.2.0",
        "data_version": table["version"],
    }
