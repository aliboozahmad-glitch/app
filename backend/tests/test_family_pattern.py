"""GENOVA Smart Algorithm: exclusively the original PDF cases, exact matching, no fallback."""
import hashlib
import itertools
import json
from pathlib import Path

import pytest

from genova.genetics.core import GeneticsInputError
from genova.traditional import family_pattern_analysis
from genova.traditional.family_pattern import DATA, load_table

ROOT = Path(__file__).resolve().parents[2]
PDF = json.loads((ROOT / "docs/source/pdf_transcription.json").read_text(encoding="utf-8"))
G = {"M": "male", "F": "female"}
FAMILIES = [list(p) for n in (1, 2, 3) for p in itertools.product(("male", "female"), repeat=n)]
OWNER = {84: "female", 87: "male", 92: "male"}


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


def test_owner_confirmed_cases():
    by_case = {c["case"]: c for c in load_table()["cases"]}
    for n, answer in OWNER.items():
        c = by_case[n]
        assert (c["result"]["single"], c["percentage"], c["source"]) == (answer, "90%", "original_pdf_owner_confirmed")
    assert all(c["percentage"] is None for n, c in by_case.items() if n not in OWNER)


def test_every_input_matches_the_pdf_exactly():
    for w, h, c in _inputs():
        assert _answer(w, h, c) == _pdf_answer(w, h, c), (w, h, c)


def test_no_matching_case_has_no_fallback():
    r = family_pattern_analysis(["male"], ["female"])  # old-app case 37, not in the PDF
    assert r["outcomes"] == [] and r["details"]["review_flags"] == ["no_matching_case"]
    assert "original_fallback" not in r["details"] and "no_matching_case" in r["limitations"]


@pytest.mark.parametrize("child,answer,rng", [(1, "male", "70\u201390%"), (2, "female", "50\u201360%")])
def test_three_plus_three_first_and_second(child, answer, rng):
    o = family_pattern_analysis(["male", "male", "female"], ["female", "male", "female"], child)["outcomes"][0]
    assert (o["key"], o["group"], o["stated_range"]) == (answer, ("first_child", "second_child")[child - 1], rng)


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


def test_deterministic():
    runs = [family_pattern_analysis(["male", "female"], ["male"]) for _ in range(5)]
    assert all(r == runs[0] for r in runs)
