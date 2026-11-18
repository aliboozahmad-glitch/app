"""GENOVA Smart Algorithm: exclusively the original PDF cases, exact matching, no fallback."""
import hashlib
import itertools
import json
from unittest.mock import patch
from pathlib import Path

import pytest

from genova.genetics.core import GeneticsInputError
from genova.traditional import family_pattern_analysis
from genova.traditional.family_pattern import DATA, load_table

ROOT = Path(__file__).resolve().parents[2]
PDF = json.loads((ROOT / "docs/source/pdf_transcription.json").read_text(encoding="utf-8"))
G = {"M": "male", "F": "female"}
FAMILIES = [list(p) for n in (1, 2, 3) for p in itertools.product(("male", "female"), repeat=n)]

def _pdf_answer(wife, husband, child):
    for e in PDF:
        if [G[x] for x in e["wife"]] == wife and [G[x] for x in e["husband"]] == husband:
            r = e["result"]
            return G[r["single"]] if "single" in r else G[r["first" if child == 1 else "second"]]
    return None


def _answer(wife, husband, child):
    outs = family_pattern_analysis(wife, husband, child)["outcomes"]
    return outs[0]["key"] if outs else None


def _inputs():
    for w in FAMILIES:
        for h in FAMILIES:
            for c in ((1, 2) if len(w) == 3 and len(h) == 3 else (None,)):
                yield w, h, c


def test_dataset_is_exactly_the_pdf():
    t = load_table()
    assert t["source_pdf_md5"] == hashlib.md5((ROOT / t["source_pdf"]).read_bytes()).hexdigest()
    nums = [c["case"] for c in t["cases"]]
    assert len(nums) == 81 and nums == [*range(1, 30), *range(41, 93)]
    assert len({(tuple(c["wife"]), tuple(c["husband"])) for c in t["cases"]}) == 81
    for c, e in zip(t["cases"], PDF, strict=True):
        assert (c["case"], c["page"]) == (e["case"], e["page"])
        assert c["wife"] == [G[x] for x in e["wife"]] and c["husband"] == [G[x] for x in e["husband"]]
        assert c["result"] == {k: G[v] for k, v in e["result"].items()}


def test_every_input_matches_the_pdf_exactly():
    for w, h, c in _inputs():
        expected = _pdf_answer(w, h, c)
        assert _answer(w, h, c) == expected, (w, h, c)


def test_no_matching_case_has_no_fallback():
    r = family_pattern_analysis(["male"], ["female"])  # old-app case 37, not in the PDF
    assert r["outcomes"] == [] and r["details"]["review_flags"] == ["no_matching_case"]
    assert "original_fallback" not in r["details"] and "no_matching_case" in r["limitations"]


@pytest.mark.parametrize("child,answer,percentage", [(1, "male", 70), (2, "female", 60)])
def test_three_plus_three_gender_is_preserved_and_percentage_is_randomized(child, answer, percentage):
    with patch("genova.traditional.family_pattern.random.choice", return_value=percentage):
        r = family_pattern_analysis(["male", "male", "female"], ["female", "male", "female"], child)
    o = r["outcomes"][0]
    assert (o["key"], o["group"], o["stated_range"], o["probability"]) == (
        answer, ("first_child" if child == 1 else "second_child"), f"{percentage}%", percentage / 100
    )
    assert "effective_case" not in r["details"] and "owner_rule" not in r["details"]
    assert "randomized_family_percentage" in r["limitations"]


def test_percentage_choices_have_requested_weighting():
    from genova.traditional.family_pattern import _random_percentage
    with patch("genova.traditional.family_pattern.random.choice", side_effect=lambda values: values[0]) as choose:
        assert _random_percentage(1) == 90
        assert choose.call_args.args[0] == (90, 70, 70)
    with patch("genova.traditional.family_pattern.random.choice", side_effect=lambda values: values[0]) as choose:
        assert _random_percentage(2) == 50
        assert choose.call_args.args[0] == (50, 60, 60)
def test_single_child_scope_ignores_child_number():
    a, b = (family_pattern_analysis(["female"], ["male", "male"], n) for n in (1, 2))
    assert a == b and a["inputs"]["child_number"] is None
    assert [(o["key"], o["group"], o["stated_range"]) for o in a["outcomes"]] == [("male", "single_child", None)]


@pytest.mark.parametrize("wife,husband,n", [([], ["male"], 1), (["male"] * 4, ["male"], 1), (["boy"], ["male"], 1),
                                            (["male"] * 3, ["male"] * 3, 3), (["male"] * 3, ["male"] * 3, None)])
def test_invalid_inputs(wife, husband, n):
    with pytest.raises(GeneticsInputError):
        family_pattern_analysis(wife, husband, n)


def test_legacy_data_deleted():
    assert [p.name for p in DATA.parent.iterdir()] == ["genova_smart_cases.json"]
    assert not (Path(__file__).parent / "fixtures").exists()
    engine = (Path(__file__).parents[1] / "genova/traditional/family_pattern.py").read_text(encoding="utf-8")
    assert "archive" not in engine and "legacy" not in engine and DATA.name == "genova_smart_cases.json"


def test_single_child_without_percentage_remains_deterministic():
    runs = [family_pattern_analysis(["male", "female"], ["male"]) for _ in range(5)]
    assert all(r == runs[0] for r in runs)
