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


def blood_type_analysis(p1_abo: str, p1_rh: str, p2_abo: str, p2_rh: str) -> dict:
    abo = _locus_scenarios(parse_abo(p1_abo), parse_abo(p2_abo), _canon_abo, abo_phenotype)
    rh = _locus_scenarios(parse_rh(p1_rh), parse_rh(p2_rh), _canon_rh, rh_phenotype)
    abo_r, rh_r = _ranges(abo), _ranges(rh)
    exact = len(abo) == 1 and len(rh) == 1
    outcomes = []
    for a, (amin, amax) in abo_r.items():
        for r, (rmin, rmax) in rh_r.items():
            lo, hi = amin * rmin, amax * rmax
            if hi == 0:
                continue
            o = {"key": f"{a}{r}", "kind": "blood_type", "group": "all_children",
                 "probability": round(float(hi), 6) if exact else None,
                 "fraction": frac_str(hi) if exact else None}
            if not exact:
                o["range"] = [round(float(lo), 6), round(float(hi), 6)]
                o["range_fraction"] = [frac_str(lo), frac_str(hi)]
            outcomes.append(o)
    outcomes.sort(key=lambda o: -(o["probability"] or o["range"][1]))
    all_types = [f"{a}{r}" for a in ("A", "B", "AB", "O") for r in ("+", "-")]
    possible = {o["key"] for o in outcomes}

    def ser(scen):
        return [{"parent1": s["parent1"], "parent2": s["parent2"],
                 "phenotypes": {k: frac_str(v) for k, v in s["phenotypes"].items()}} for s in scen]

    details = {"possible_types": [t for t in all_types if t in possible],
               "impossible_types": [t for t in all_types if t not in possible],
               "abo_scenarios": ser(abo), "rh_scenarios": ser(rh), "exact": exact}
    return make_result(
        "blood_type", "established", "blood_type_exact" if exact else "blood_type_scenarios",
        {"parent1": {"abo": p1_abo, "rh": p1_rh}, "parent2": {"abo": p2_abo, "rh": p2_rh}},
        outcomes, ["standard_abo_rh_model", "mendelian_segregation"] + ([] if exact else ["phenotype_genotype_unknown"]),
        ["abo_rare_exceptions"], REFS, details)
