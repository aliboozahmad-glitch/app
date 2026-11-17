"""Owner's family-pattern table: reproduced exactly, deterministic, flagged where unconfirmed."""
import json
from pathlib import Path

import pytest

from genova.genetics import GeneticsInputError
from genova.i18n import LANGS, T, localize_result
from genova.traditional import family_pattern_analysis
from genova.traditional.family_pattern import all_entries, legacy_order, load_table

LEGACY = Path(__file__).parent / "fixtures" / "legacy_family_pattern_raw.json"  # parsed from the original file
SRC = Path(__file__).resolve().parents[1] / "genova" / "traditional" / "family_pattern.py"


def legacy_dict():
    """Rebuild the original Python dict (later keys overwrite earlier ones)."""
    raw = json.loads(LEGACY.read_text(encoding="utf-8"))["PREDICTION_TABLE_EN"]
    return {tuple(e["key"]): e["result"] for e in raw}


BASELINE = Path(__file__).parent / "fixtures" / "family_pattern_results_baseline.json"


PDF_ONLY = [*range(61, 69), 81, 82, 83, 85, 86, 88, 89, 90, 91]


def _case_numbers(entries, origin=None):
    return sorted(c["case"] for c in entries if origin is None or c["origin"] == origin)


def test_case_numbers_and_origins():
    t = load_table()
    assert _case_numbers(t["cases"]) == sorted([*range(1, 30), *range(41, 61), *range(69, 81), *PDF_ONLY])
    assert _case_numbers(t["cases"], "original_pdf") == PDF_ONLY
    assert not {84, 87, 92} & set(_case_numbers(all_entries()))
    assert _case_numbers(t["old_app_only_cases"], "old_app_only") == list(range(30, 41))


def test_all_72_original_entries_preserved_unchanged():
    cases = legacy_order()
    assert len(cases) == 72
    if LEGACY.exists():
        raw = json.loads(LEGACY.read_text(encoding="utf-8"))["PREDICTION_TABLE_EN"]
        assert [(c["pattern"], c["result"]) for c in cases] == [(e["key"], e["result"]) for e in raw]


def test_wife_and_husband_stored_separately():
    for c in all_entries():
        assert c["wife"] + c["husband"] == c["pattern"] and 1 <= len(c["wife"]) <= 3 and 1 <= len(c["husband"]) <= 3


def test_every_answer_unchanged_by_split():
    base = json.loads(BASELINE.read_text(encoding="utf-8"))["results"]
    assert len(base) == 392
    for k, v in base.items():
        w, h, n = k.split("|")
        outs = family_pattern_analysis(w.split(","), h.split(","), int(n))["outcomes"]
        assert (outs[0]["key"] if outs else None) == v, k


@pytest.mark.skipif(not LEGACY.exists(), reason="legacy extract not present")
def test_every_lookup_matches_the_original_app():
    for key, result in legacy_dict().items():
        for split in range(1, len(key)):
            wife, husband = list(key[:split]), list(key[split:])
            if len(wife) > 3 or len(husband) > 3:
                continue
            for n, slot in ((1, "first"), (2, "second")):
                r = family_pattern_analysis(wife, husband, n)
                assert [o["key"] for o in r["outcomes"]] == [result[slot]], (wife, husband, n)


def test_three_plus_three_case_1_and_no_flags():
    r = family_pattern_analysis(["male", "male", "female"], ["male", "male", "female"], 1)
    assert [o["key"] for o in r["outcomes"]] == ["male"]
    assert r["details"]["effective_case"] == 1 and r["details"]["review_flags"] == []
    assert r["certainty"] == "traditional_belief"


def test_duplicate_pattern_prefers_exact_family_split():
    r = family_pattern_analysis(["male", "male"], ["male", "male"], 1)
    assert r["details"]["matched_cases"] == [41, 78, 90] and r["details"]["effective_case"] == 41
    assert r["details"]["review_flags"] == ["duplicate_pattern"] and r["details"]["answer_borrowed"] is False


def test_one_plus_two_exact_case_54():
    r = family_pattern_analysis(["female"], ["male", "male"], 1)
    assert r["details"]["effective_case"] == 54 and r["details"]["review_flags"] == ["duplicate_pattern"]
    assert r["details"]["answer_borrowed"] is False


@pytest.mark.parametrize("wife,husband,case,answer", [
    (["male", "female", "male"], ["female"], 75, "male"),  # PDF 84 says girl: not applied yet
    (["female", "male", "female"], ["male"], 72, "female"),  # PDF 87 says boy: not applied yet
])
def test_answer_from_other_case_shows_source(wife, husband, case, answer):
    r = family_pattern_analysis(wife, husband, 1)
    d = r["details"]
    assert d["effective_case"] == case and d["answer_borrowed"] is True
    assert "answer_from_other_case" in d["review_flags"] and d["source_case"]["case"] == case
    assert [o["key"] for o in r["outcomes"]] == [answer]


def test_pdf_92_still_not_in_table():
    r = family_pattern_analysis(["male", "female", "female"], ["male"], 1)
    assert r["outcomes"] == [] and r["details"]["review_flags"] == ["not_in_table"]


@pytest.mark.parametrize("wife,husband,case", [(["male"], ["female"], 37), (["female", "female", "male"],
                                                                         ["male", "female", "male"], 30)])
def test_old_app_only_labelled(wife, husband, case):
    d = family_pattern_analysis(wife, husband, 1)["details"]
    assert d["effective_case"] == case and d["origin"] == "old_app_only" and "old_app_only" in d["review_flags"]


def test_unknown_pattern_gives_no_answer_and_no_default():
    r = family_pattern_analysis(["male", "female", "male"], ["female", "female", "female"], 1)
    assert r["outcomes"] == [] and r["details"]["review_flags"] == ["not_in_table"]


def test_no_randomness_and_no_percentages():
    src = SRC.read_text()
    assert "random" not in src.replace("randomness", "").replace("random percentages", "")
    runs = [family_pattern_analysis(["female", "male"], ["male", "female"], 2) for _ in range(5)]
    assert all(r == runs[0] for r in runs)
    assert all(o["probability"] is None for o in runs[0]["outcomes"])


def test_statistic_kept_separate():
    r = family_pattern_analysis(["male"], ["female"], 1)
    assert r["analysis_type"] == "family_pattern" and r["details"]["statistic_separate"] is True
    assert "traditional_not_scientific" in r["limitations"]


@pytest.mark.parametrize("wife,husband,n", [([], ["male"], 1), (["male"] * 4, ["male"], 1), (["boy"], ["male"], 1),
                                            (["male"] * 3, ["male"] * 3, 3), (["male"] * 3, ["male"] * 3, None)])
def test_invalid(wife, husband, n):
    with pytest.raises(GeneticsInputError):
        family_pattern_analysis(wife, husband, n)


def test_all_keys_translated():
    for w, h in ((["male"], ["female"]), (["male", "male"], ["male", "male"]), (["female"], ["male", "male"]),
                 (["male", "female", "male"], ["female"]),
                 (["male", "female", "male"], ["female", "female", "female"])):
        r = family_pattern_analysis(w, h, 1)
        groups = [o["group"] for o in r["outcomes"]]
        for k in [r["certainty"], r["method"], *r["assumptions"], *r["limitations"], *groups]:
            assert k in T, k
        for lang in LANGS:
            assert localize_result(r, lang)["references"]


@pytest.mark.parametrize("wife,husband,case,answer", [
    (["female", "female"], ["female"], 61, "female"), (["male", "female"], ["male"], 68, "male"),
    (["female", "female", "female"], ["female"], 81, "female"), (["female", "male", "male"], ["male"], 91, "male"),
])
def test_pdf_only_cases_exact_and_unborrowed(wife, husband, case, answer):
    r = family_pattern_analysis(wife, husband)
    d = r["details"]
    assert d["effective_case"] == case and d["origin"] == "original_pdf" and d["answer_borrowed"] is False
    assert "answer_from_other_case" not in d["review_flags"]
    assert [(o["key"], o["group"]) for o in r["outcomes"]] == [(answer, "single_child")]


def test_single_child_scope_ignores_child_number():
    a = family_pattern_analysis(["male"], ["female"], 1)
    b = family_pattern_analysis(["male"], ["female"], 2)
    assert a == b and a["inputs"]["child_number"] is None and a["details"]["prediction_scope"] == "single_child"


def test_three_plus_three_keeps_first_and_second():
    w, h = ["male", "male", "female"], ["female", "male", "female"]
    groups = [family_pattern_analysis(w, h, n)["outcomes"][0] for n in (1, 2)]
    assert [(o["key"], o["group"]) for o in groups] == [("male", "first_child"), ("female", "second_child")]


def test_non_three_plus_three_entries_have_one_answer():
    for c in all_entries():
        if not (len(c["wife"]) == 3 and len(c["husband"]) == 3):
            assert c["result"]["first"] == c["result"]["second"], c["case"]
