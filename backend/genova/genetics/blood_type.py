"""ABO and RhD blood type inheritance (standard two-locus model, independent assortment)."""
from fractions import Fraction
from itertools import product

from .core import GeneticsInputError, frac_str, make_result, punnett, regroup

ABO_BY_PHENOTYPE = {"A": ["AA", "AO"], "B": ["BB", "BO"], "AB": ["AB"], "O": ["OO"]}
ABO_GENOTYPES = {"AA", "AO", "BB", "BO", "AB", "OO"}
RH_BY_PHENOTYPE = {"+": ["DD", "Dd"], "-": ["dd"]}
RH_GENOTYPES = {"DD", "Dd", "dd"}
REFS = ["medlineplus-blood-typing", "ncbi-dean-blood-groups"]


def _canon_abo(a, b):
    return "".join(sorted([a, b], key="ABO".index))


def _canon_rh(a, b):
    return "".join(sorted([a, b], key=lambda x: x.islower()))


def abo_phenotype(g: str) -> str:
    s = set(g)
    if s == {"A", "B"}:
        return "AB"
    return "A" if "A" in s else "B" if "B" in s else "O"


def rh_phenotype(g: str) -> str:
    return "+" if "D" in g else "-"


def parse_abo(value: str) -> list:
    v = value.strip().upper()
    if v in ABO_BY_PHENOTYPE:
        return ABO_BY_PHENOTYPE[v]
    if len(v) == 2 and set(v) <= set("ABO") and _canon_abo(*v) in ABO_GENOTYPES:
        return [_canon_abo(*v)]
    raise GeneticsInputError("invalid_abo")


def parse_rh(value: str) -> list:
    v = value.strip()
    if v in RH_BY_PHENOTYPE:
        return RH_BY_PHENOTYPE[v]
    if len(v) == 2 and _canon_rh(*v) in RH_GENOTYPES:
        return [_canon_rh(*v)]
    raise GeneticsInputError("invalid_rh")


def _locus_scenarios(options1, options2, canon, pheno):
    scenarios = []
    for g1, g2 in product(options1, options2):
        _, dist = punnett(list(g1), list(g2), canon)
        scenarios.append({"parent1": g1, "parent2": g2, "phenotypes": regroup(dist, pheno)})
    return scenarios


def _ranges(scenarios):
    keys = sorted({k for s in scenarios for k in s["phenotypes"]})
    return {k: (min(s["phenotypes"].get(k, Fraction(0)) for s in scenarios),
                max(s["phenotypes"].get(k, Fraction(0)) for s in scenarios)) for k in keys}


ALL_TYPES = [f"{a}{r}" for a in ("A", "B", "AB", "O") for r in ("+", "-")]


def _exact_outcome(key, p):
    return {"key": key, "kind": "blood_type", "group": "all_children",
            "probability": round(float(p), 6), "fraction": frac_str(p)}


def _range_outcome(key, lo, hi):
    return {"key": key, "kind": "blood_type", "group": "all_children", "probability": None, "fraction": None,
            "range": [round(float(lo), 6), round(float(hi), 6)], "range_fraction": [frac_str(lo), frac_str(hi)]}


def _combined_outcomes(abo_r, rh_r, exact):
    """ABO and RhD are independent loci, so bounds multiply."""
    outcomes = []
    for a, (amin, amax) in abo_r.items():
        for r, (rmin, rmax) in rh_r.items():
            lo, hi = amin * rmin, amax * rmax
            if hi > 0:
                outcomes.append(_exact_outcome(f"{a}{r}", hi) if exact else _range_outcome(f"{a}{r}", lo, hi))
    return sorted(outcomes, key=lambda o: -(o["probability"] or o["range"][1]))


def _serialise(scenarios):
    return [{"parent1": s["parent1"], "parent2": s["parent2"],
             "phenotypes": {k: frac_str(v) for k, v in s["phenotypes"].items()}} for s in scenarios]


def blood_type_analysis(p1_abo: str, p1_rh: str, p2_abo: str, p2_rh: str) -> dict:
    abo = _locus_scenarios(parse_abo(p1_abo), parse_abo(p2_abo), _canon_abo, abo_phenotype)
    rh = _locus_scenarios(parse_rh(p1_rh), parse_rh(p2_rh), _canon_rh, rh_phenotype)
    exact = len(abo) == 1 and len(rh) == 1
    outcomes = _combined_outcomes(_ranges(abo), _ranges(rh), exact)
    possible = {o["key"] for o in outcomes}
    details = {"possible_types": [t for t in ALL_TYPES if t in possible],
               "impossible_types": [t for t in ALL_TYPES if t not in possible],
               "abo_scenarios": _serialise(abo), "rh_scenarios": _serialise(rh), "exact": exact}
    assumptions = ["standard_abo_rh_model", "mendelian_segregation"]
    if not exact:
        assumptions.append("phenotype_genotype_unknown")
    return make_result(
        "blood_type", "established", "blood_type_exact" if exact else "blood_type_scenarios",
        {"parent1": {"abo": p1_abo, "rh": p1_rh}, "parent2": {"abo": p2_abo, "rh": p2_rh}},
        outcomes, assumptions, ["abo_rare_exceptions"], REFS, details)
