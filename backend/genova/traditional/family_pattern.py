"""GENOVA Smart Algorithm: the owner's original PDF cases, matched exactly. Not part of genova.genetics.

Sole data source: data/genova_smart_cases.json (the 81 numbered entries of the original PDF, numbers 1-92 with
30-40 absent in the PDF). Exact wife's family + husband's family match only; no fallback, no borrowing,
no randomness. Only 3 + 3 families predict a first and second child; all others predict one child.
"""
import json
from functools import lru_cache
from pathlib import Path

from ..genetics.core import GeneticsInputError

GENDERS = ("male", "female")
DATA = Path(__file__).parent / "data" / "genova_smart_cases.json"


@lru_cache(maxsize=1)
def load_table() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def is_two_child_section(wife: list, husband: list) -> bool:
    return len(wife) == 3 and len(husband) == 3


def _validate(wife: list, husband: list, child_number: int | None) -> None:
    for family in (wife, husband):
        if not 1 <= len(family) <= 3 or any(g not in GENDERS for g in family):
            raise GeneticsInputError("invalid_family_pattern")
    if is_two_child_section(wife, husband) and child_number not in (1, 2):
        raise GeneticsInputError("child_number_required")


def find_case(wife: list, husband: list) -> dict | None:
    return next((c for c in load_table()["cases"] if c["wife"] == wife and c["husband"] == husband), None)


def _outcome(case: dict, two_child: bool, child_number: int | None) -> dict:
    ranges = load_table()["pdf_stated_ranges"]
    if two_child:
        group = "first_child" if child_number == 1 else "second_child"
        key = case["result"]["first" if child_number == 1 else "second"]
    else:
        group, key = "single_child", case["result"]["single"]
    return {"key": key, "kind": "traditional", "group": group, "probability": None, "fraction": None,
            "stated_range": case["percentage"] or (ranges[group] if two_child else None)}


def family_pattern_analysis(wife: list, husband: list, child_number: int | None = None) -> dict:
    _validate(wife, husband, child_number)
    two_child = is_two_child_section(wife, husband)
    child_number = child_number if two_child else None
    table = load_table()
    case = find_case(wife, husband)
    details = {"entered_split": [len(wife), len(husband)],
               "prediction_scope": "first_and_second_child" if two_child else "single_child",
               "statistic_separate": True}
    limitations = ["traditional_not_scientific", "no_confidence_score"]
    outcomes = []
    if case:
        details |= {"effective_case": case["case"], "pdf_page": case["page"], "case_source": case["source"],
                    "review_flags": []}
        outcomes.append(_outcome(case, two_child, child_number))
    else:
        details["review_flags"] = ["no_matching_case"]
        limitations.append("no_matching_case")
    return {
        "analysis_type": "family_pattern",
        "certainty": "traditional_belief",
        "method": "genova_smart_algorithm",
        "inputs": {"wife": wife, "husband": husband, "child_number": child_number},
        "outcomes": outcomes,
        "assumptions": ["traditional_table_as_provided"],
        "limitations": ["not_diagnosis", *limitations],
        "references": ["genova-smart-pdf"],
        "details": details,
        "engine_version": "genova-smart 2.0.0",
        "data_version": table["version"],
    }
