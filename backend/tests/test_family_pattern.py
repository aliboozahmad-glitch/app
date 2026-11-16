"""Owner's family-pattern table: reproduced exactly, deterministic, flagged where unconfirmed."""
import json
from pathlib import Path

import pytest

from genova.genetics import GeneticsInputError
from genova.i18n import LANGS, T, localize_result
from genova.traditional import family_pattern_analysis
from genova.traditional.family_pattern import load_table

LEGACY = Path(__file__).parent / "fixtures" / "legacy_family_pattern_raw.json"  # parsed from the original file
SRC = Path(__file__).resolve().parents[1] / "genova" / "traditional" / "family_pattern.py"


def legacy_dict():
    """Rebuild the original Python dict (later keys overwrite earlier ones)."""
    raw = json.loads(LEGACY.read_text(encoding="utf-8"))["PREDICTION_TABLE_EN"]
    return {tuple(e["key"]): e["result"] for e in raw}


def test_all_72_original_entries_preserved_unchanged():
    cases = load_table()["cases"]
    assert len(cases) == 72
    assert sorted(c["case"] for c in cases) == [*range(1, 61), *range(69, 81)]
    if LEGACY.exists():
        raw = json.loads(LEGACY.read_text(encoding="utf-8"))["PREDICTION_TABLE_EN"]
        assert [(c["pattern"], c["result"]) for c in cases] == [(e["key"], e["result"]) for e in raw]


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


def test_duplicate_pattern_uses_later_entry_and_is_flagged():
    r = family_pattern_analysis(["male", "male"], ["male", "male"], 1)
    assert r["details"]["matched_cases"] == [41, 78] and r["details"]["effective_case"] == 78
    assert "duplicate_pattern" in r["details"]["review_flags"]


def test_one_plus_two_split_flagged_unconfirmed():
    r = family_pattern_analysis(["female"], ["male", "male"], 1)
    assert r["details"]["effective_case"] == 54 and "split_unconfirmed" in r["details"]["review_flags"]


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
                                            (["male"], ["male"], 3)])
def test_invalid(wife, husband, n):
    with pytest.raises(GeneticsInputError):
        family_pattern_analysis(wife, husband, n)


def test_all_keys_translated():
    for w, h in ((["male"], ["female"]), (["male", "male"], ["male", "male"]), (["female"], ["male", "male"]),
                 (["male", "female", "male"], ["female", "female", "female"])):
        r = family_pattern_analysis(w, h, 1)
        groups = [o["group"] for o in r["outcomes"]]
        for k in [r["certainty"], r["method"], *r["assumptions"], *r["limitations"], *groups]:
            assert k in T, k
        for lang in LANGS:
            assert localize_result(r, lang)["references"]
