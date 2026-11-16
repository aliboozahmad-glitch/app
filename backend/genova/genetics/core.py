from collections import defaultdict
from fractions import Fraction
from itertools import product

ENGINE_VERSION = "genova-genetics 1.0.0"
CERTAINTY_TIERS = (
    "established", "population_estimate", "statistical_estimate", "uncertain_estimate", "population_statistic",
)


class GeneticsInputError(ValueError):
    """Raised for inputs the engine cannot interpret. Message is a stable error key."""


def frac_str(p: Fraction) -> str:
    return str(p.numerator) if p.denominator == 1 else f"{p.numerator}/{p.denominator}"


def outcome(key: str, p: Fraction, kind: str = "phenotype", group: str = "all_children") -> dict:
    return {"key": key, "kind": kind, "group": group, "probability": round(float(p), 6), "fraction": frac_str(p)}


def punnett(gametes_a: list, gametes_b: list, combine) -> tuple[dict, dict]:
    """Cross two parents whose gametes each occur with equal probability."""
    cells = [[combine(a, b) for a in gametes_a] for b in gametes_b]
    weight = Fraction(1, len(gametes_a) * len(gametes_b))
    dist = defaultdict(Fraction)
    for a, b in product(gametes_a, gametes_b):
        dist[combine(a, b)] += weight
    grid = {"columns": gametes_a, "rows": gametes_b, "cells": cells}
    return grid, dict(dist)


def regroup(dist: dict, fn) -> dict:
    out = defaultdict(Fraction)
    for k, p in dist.items():
        out[fn(k)] += p
    return dict(out)


def normalise(dist: dict) -> dict:
    total = sum(dist.values())
    return {k: v / total for k, v in dist.items()}


def sorted_outcomes(dist: dict, kind: str, group: str = "all_children") -> list:
    items = sorted(dist.items(), key=lambda kv: (-kv[1], kv[0]))
    return [outcome(k, p, kind, group) for k, p in items if p > 0]


def make_result(analysis_type, certainty, method, inputs, outcomes, assumptions, limitations, references,
                details=None, data_version=None) -> dict:
    assert certainty in CERTAINTY_TIERS
    return {
        "analysis_type": analysis_type,
        "certainty": certainty,
        "method": method,
        "inputs": inputs,
        "outcomes": outcomes,
        "assumptions": assumptions,
        "limitations": ["not_diagnosis", *limitations],
        "references": references,
        "details": details or {},
        "engine_version": ENGINE_VERSION,
        "data_version": data_version,
    }
