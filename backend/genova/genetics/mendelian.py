"""Single-gene Mendelian crosses (Punnett squares)."""
from fractions import Fraction

from .core import GeneticsInputError, make_result, punnett, regroup, sorted_outcomes

AUTOSOMAL_GENOTYPES = {
    "autosomal_dominant": ("AA", "Aa", "aa"),
    "autosomal_recessive": ("AA", "Aa", "aa"),
    "codominant": ("AA", "AB", "BB"),
    "incomplete_dominance": ("AA", "AB", "BB"),
}
X_MOTHER = ("XAXA", "XAXa", "XaXa")
X_FATHER = ("XAY", "XaY")
X_MODES = ("x_linked_recessive", "x_linked_dominant")
MODES = (*AUTOSOMAL_GENOTYPES.keys(), *X_MODES)

REFS = ["medlineplus-inheritance-patterns"]


def _canon_auto(a: str, b: str) -> str:
    # Uppercase allele first (Aa), then alphabetical (AB).
    return "".join(sorted([a, b], key=lambda x: (x.islower(), x)))


def _x_alleles(genotype: str) -> list:
    out, i = [], 0
    while i < len(genotype):
        if genotype[i] == "Y":
            out.append("Y")
            i += 1
        else:
            out.append(genotype[i:i + 2])
            i += 2
    return out


def _canon_x(a: str, b: str) -> str:
    alleles = sorted([a, b], key=lambda x: (x == "Y", x[-1:].islower(), x))
    return "".join(alleles)


def autosomal_phenotype(mode: str, g: str) -> str:
    if mode == "autosomal_dominant":
        return "shows_trait" if "A" in g else "no_trait"
    if mode == "autosomal_recessive":
        return {"aa": "shows_trait", "Aa": "carrier_no_trait", "AA": "no_trait_non_carrier"}[g]
    if g == "AB":
        return "both_expressed" if mode == "codominant" else "intermediate"
    return "allele_A_trait" if g == "AA" else "allele_B_trait"


def x_phenotype(mode: str, g: str) -> str:
    is_son = g.endswith("Y")
    trait_allele = "Xa" if mode == "x_linked_recessive" else "XA"
    n = _x_alleles(g).count(trait_allele)
    if mode == "x_linked_dominant":
        return "shows_trait" if n else "no_trait"
    if is_son:
        return "shows_trait" if n else "no_trait"
    return {2: "shows_trait", 1: "carrier_no_trait", 0: "no_trait_non_carrier"}[n]


def cross_autosomal(mode: str, g1: str, g2: str) -> dict:
    valid = AUTOSOMAL_GENOTYPES[mode]
    if len(g1) != 2 or len(g2) != 2:
        raise GeneticsInputError("invalid_genotype")
    g1, g2 = _canon_auto(*g1), _canon_auto(*g2)
    if g1 not in valid or g2 not in valid:
        raise GeneticsInputError("invalid_genotype")
    grid, geno = punnett(list(g1), list(g2), _canon_auto)
    return {"grid": grid, "genotypes": geno, "phenotypes": regroup(geno, lambda g: autosomal_phenotype(mode, g))}


def cross_x(mode: str, mother: str, father: str) -> dict:
    if mother not in X_MOTHER or father not in X_FATHER:
        raise GeneticsInputError("invalid_genotype")
    grid, geno = punnett(_x_alleles(mother), _x_alleles(father), _canon_x)
    out = {"grid": grid}
    for group, is_son in (("sons", True), ("daughters", False)):
        sub = {g: p * 2 for g, p in geno.items() if g.endswith("Y") == is_son}  # condition on sex (each 1/2)
        out[group] = {"genotypes": sub, "phenotypes": regroup(sub, lambda g: x_phenotype(mode, g))}
    return out


def mendelian_analysis(mode: str, parent1: str, parent2: str) -> dict:
    """parent1/parent2 are genotypes. For X-linked modes parent1 = mother, parent2 = father."""
    if mode not in MODES:
        raise GeneticsInputError("invalid_mode")
    inputs = {"mode": mode, "parent1": parent1, "parent2": parent2}
    assumptions = ["stated_genotypes_correct", "mendelian_segregation", "complete_penetrance", "no_new_mutation"]
    if mode in X_MODES:
        c = cross_x(mode, parent1, parent2)
        outcomes = []
        for group in ("sons", "daughters"):
            outcomes += sorted_outcomes(c[group]["phenotypes"], "phenotype", group)
            outcomes += sorted_outcomes(c[group]["genotypes"], "genotype", group)
        return make_result("mendelian", "established", "punnett_x_linked", inputs, outcomes,
                           assumptions, ["x_results_per_sex"], REFS, {"grid": c["grid"]})
    c = cross_autosomal(mode, parent1, parent2)
    outcomes = sorted_outcomes(c["phenotypes"], "phenotype") + sorted_outcomes(c["genotypes"], "genotype")
    return make_result("mendelian", "established", "punnett_autosomal", inputs, outcomes,
                       assumptions, [], REFS, {"grid": c["grid"]})


def total(dist: dict) -> Fraction:
    return sum(dist.values(), Fraction(0))
