"""Integrity rules: no randomness, probabilities sum to 1, every number has a source, every key is translated."""
import itertools
from fractions import Fraction
from pathlib import Path

from genova.genetics import (
    blood_type_analysis,
    carrier_analysis,
    height_analysis,
    mendelian_analysis,
    pigmentation_analysis,
    sex_ratio_analysis,
)
from genova.genetics.data_loader import disease_list, load_references
from genova.genetics.mendelian import AUTOSOMAL_GENOTYPES, X_FATHER, X_MOTHER
from genova.i18n import LANGS, T, localize_result

ENGINE_DIR = Path(__file__).resolve().parents[1] / "genova" / "genetics"


def test_engine_has_no_randomness():
    for f in ENGINE_DIR.glob("*.py"):
        src = f.read_text()
        assert "import random" not in src and "from random" not in src and "secrets" not in src, f.name


def _sums(result):
    groups = {}
    for o in result["outcomes"]:
        if o["kind"] in ("phenotype", "genotype") and o["fraction"]:
            groups.setdefault((o["kind"], o["group"]), Fraction(0))
            groups[(o["kind"], o["group"])] += Fraction(o["fraction"])
    return groups


def all_results():
    for mode, gs in AUTOSOMAL_GENOTYPES.items():
        for a, b in itertools.product(gs, gs):
            yield mendelian_analysis(mode, a, b)
    for mode in ("x_linked_recessive", "x_linked_dominant"):
        for m, f in itertools.product(X_MOTHER, X_FATHER):
            yield mendelian_analysis(mode, m, f)
    for p in itertools.product(["A", "B", "AB", "O", "AO", "BB"], ["+", "-", "Dd"], ["A", "O", "BO"], ["+", "dd"]):
        yield blood_type_analysis(*p)
    for d in disease_list():
        ar = d["inheritance"] == "autosomal_recessive"
        ms = ["affected", "carrier", "non_carrier", "unknown"]
        fs = ms if ar else ["affected", "unaffected", "unknown"]
        for m, f in itertools.product(ms, fs):
            yield carrier_analysis(d["id"], m, f, "gulf")
    yield height_analysis(170, 170)
    yield sex_ratio_analysis()
    yield pigmentation_analysis("eye_color", "green", "hazel")
    yield pigmentation_analysis("hair_color", "black", "blonde")


def test_probabilities_sum_to_one():
    for r in all_results():
        for key, total in _sums(r).items():
            assert total == 1, (r["inputs"], key, total)
        for s in r["details"].get("scenarios", []):
            per_group = {}
            for o in s["outcomes"]:
                per_group[o["group"]] = per_group.get(o["group"], Fraction(0)) + Fraction(o["fraction"])
            assert all(v == 1 for v in per_group.values())


def test_blood_exact_sums_to_one():
    r = blood_type_analysis("AO", "Dd", "BO", "Dd")
    assert sum(Fraction(o["fraction"]) for o in r["outcomes"]) == 1


def test_deterministic():
    assert list(all_results()) == list(all_results())


def test_every_result_has_references_and_disclaimer():
    refs = load_references()
    for r in all_results():
        assert r["references"], r["analysis_type"]
        assert all(ref in refs for ref in r["references"])
        assert r["limitations"][0] == "not_diagnosis"


def test_disease_data_integrity():
    refs = load_references()
    for d in disease_list():
        assert set(d["names"]) == set(LANGS)
        assert d["references"] and all(r in refs for r in d["references"])
        for entry in d["regional"]:
            assert entry["status"] in ("draft", "validated")
            assert entry["source"] in refs
            if entry["status"] == "validated":
                assert entry.get("reviewed_by"), d["id"]


def test_references_have_url_and_link_status():
    for r in load_references().values():
        assert r["url"].startswith("https://") and r["link_check"] in ("verified_2026_06", "manual_check_required")


def test_every_emitted_key_is_translated():
    for r in all_results():
        keys = {r["certainty"], r["method"], *r["assumptions"], *r["limitations"]}
        keys |= {o["group"] for o in r["outcomes"]}
        keys |= {o["key"] for o in r["outcomes"] if o["kind"] not in ("genotype", "blood_type")}
        for k in keys:
            assert k in T, k
        for lang in LANGS:
            localize_result(r, lang)
    assert all(len(v) == 3 and all(v) for v in T.values())
