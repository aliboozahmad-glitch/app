"""Disease carrier risk: exact Mendelian results for confirmed statuses, conditional scenarios
for unknown statuses, and a population estimate ONLY when a validated regional frequency exists."""
from fractions import Fraction
from itertools import product

from .core import GeneticsInputError, frac_str, make_result, sorted_outcomes
from .data_loader import load_diseases
from .mendelian import cross_autosomal, cross_x

AR_STATUS = {"affected": ["aa"], "carrier": ["Aa"], "non_carrier": ["AA"], "unknown": ["Aa", "AA"]}
X_MOTHER_STATUS = {"affected": ["XaXa"], "carrier": ["XAXa"], "non_carrier": ["XAXA"], "unknown": ["XAXa", "XAXA"]}
X_FATHER_STATUS = {"affected": ["XaY"], "unaffected": ["XAY"], "unknown": ["XAY", "XaY"]}
CARRIER_GENOTYPES = {"Aa", "XAXa"}
AFFECTED_FATHER = "XaY"

PHENO_MAP = {"shows_trait": "affected", "carrier_no_trait": "carrier", "no_trait_non_carrier": "unaffected_non_carrier",
             "no_trait": "unaffected"}


def _disease_outcomes(disease, cross, groups):
    out = []
    for group, ph in groups(cross):
        mapped = {}
        for k, p in ph.items():
            key = PHENO_MAP[k]
            if key == "carrier" and disease.get("female_variable_expression"):
                key = "heterozygous_variable"
            mapped[key] = mapped.get(key, Fraction(0)) + p
        out += sorted_outcomes(mapped, "phenotype", group)
    return out


def _validated_region(disease, region):
    for r in disease.get("regional", []):
        if r["region"] == region and r.get("status") == "validated":
            return r
    return None


def _weight(genotype, region_entry, parent):
    """Population probability of a genotype for an unknown-status parent (validated data only)."""
    if parent == "father_x":
        f = Fraction(region_entry["affected_male_frequency"])
        return f if genotype == AFFECTED_FATHER else 1 - f
    c = Fraction(region_entry["carrier_frequency"])
    return c if genotype in CARRIER_GENOTYPES else 1 - c


def carrier_analysis(disease_id: str, mother_status: str, father_status: str, region: str | None = None,
                     diseases: dict | None = None) -> dict:
    diseases = diseases or load_diseases()
    disease = diseases.get(disease_id)
    if not disease:
        raise GeneticsInputError("unknown_disease")
    ar = disease["inheritance"] == "autosomal_recessive"
    m_map, f_map = (AR_STATUS, AR_STATUS) if ar else (X_MOTHER_STATUS, X_FATHER_STATUS)
    if mother_status not in m_map or father_status not in f_map:
        raise GeneticsInputError("invalid_status")

    def run(m, f):
        if ar:
            c = cross_autosomal("autosomal_recessive", m, f)
            return _disease_outcomes(disease, c, lambda c: [("all_children", c["phenotypes"])])
        c = cross_x("x_linked_recessive", m, f)
        return _disease_outcomes(disease, c, lambda c: [(g, c[g]["phenotypes"]) for g in ("sons", "daughters")])

    scenarios = [{"mother_genotype": m, "father_genotype": f, "outcomes": run(m, f)}
                 for m, f in product(m_map[mother_status], f_map[father_status])]
    inputs = {"disease_id": disease_id, "mother_status": mother_status, "father_status": father_status,
              "region": region}
    assumptions = ["stated_status_correct", "mendelian_segregation", "complete_penetrance"]
    limitations = list(disease.get("limitations", []))
    if "non_carrier" in (mother_status, father_status):
        limitations.append("negative_test_residual")
    refs = disease["references"]
    data_version = diseases.get("_version")
    common = {"disease": disease_id, "inheritance": disease["inheritance"], "scenarios": scenarios}

    unknown = "unknown" in (mother_status, father_status)
    if not unknown:
        return make_result("carrier_risk", "established", "carrier_exact", inputs, scenarios[0]["outcomes"],
                           assumptions, limitations, refs, common, data_version)

    assumptions.append("unknown_parent_unaffected")
    entry = _validated_region(disease, region) if region else None
    if entry is None:
        common["population_estimate"] = {"available": False, "reason": "region_data_unvalidated"}
        return make_result("carrier_risk", "established", "carrier_conditional", inputs, [],
                           assumptions, limitations + ["region_data_unvalidated"], refs, common, data_version)

    totals = {}
    for m, f in product(m_map[mother_status], f_map[father_status]):
        w = Fraction(1)
        if mother_status == "unknown":
            w *= _weight(m, entry, "mother")
        if father_status == "unknown":
            w *= _weight(f, entry, "father_x" if not ar else "father")
        for o in run(m, f):
            k = (o["group"], o["key"])
            totals[k] = totals.get(k, Fraction(0)) + w * Fraction(o["fraction"])
    outcomes = [{"key": k, "kind": "phenotype", "group": g, "probability": round(float(p), 6), "fraction": frac_str(p)}
                for (g, k), p in sorted(totals.items(), key=lambda kv: -kv[1]) if p > 0]
    common["population_estimate"] = {"available": True, "region": region, "source": entry["source"]}
    return make_result("carrier_risk", "population_estimate", "carrier_population", inputs, outcomes,
                       assumptions + ["regional_frequency_applies"], limitations, refs + [entry["source"]],
                       common, data_version)
