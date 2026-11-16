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


def _resolve(disease_id, mother_status, father_status, diseases):
    disease = diseases.get(disease_id)
    if not disease:
        raise GeneticsInputError("unknown_disease")
    ar = disease["inheritance"] == "autosomal_recessive"
    m_map, f_map = (AR_STATUS, AR_STATUS) if ar else (X_MOTHER_STATUS, X_FATHER_STATUS)
    if mother_status not in m_map or father_status not in f_map:
        raise GeneticsInputError("invalid_status")
    return disease, ar, m_map[mother_status], f_map[father_status]


def _run_cross(disease, ar, mother_genotype, father_genotype):
    if ar:
        c = cross_autosomal("autosomal_recessive", mother_genotype, father_genotype)
        return _disease_outcomes(disease, c, lambda c: [("all_children", c["phenotypes"])])
    c = cross_x("x_linked_recessive", mother_genotype, father_genotype)
    return _disease_outcomes(disease, c, lambda c: [(g, c[g]["phenotypes"]) for g in ("sons", "daughters")])


def _scenario_weight(scenario, statuses, entry, ar):
    w = Fraction(1)
    if statuses[0] == "unknown":
        w *= _weight(scenario["mother_genotype"], entry, "mother")
    if statuses[1] == "unknown":
        w *= _weight(scenario["father_genotype"], entry, "father" if ar else "father_x")
    return w


def _population_outcomes(scenarios, statuses, entry, ar):
    totals = {}
    for s in scenarios:
        w = _scenario_weight(s, statuses, entry, ar)
        for o in s["outcomes"]:
            k = (o["group"], o["key"])
            totals[k] = totals.get(k, Fraction(0)) + w * Fraction(o["fraction"])
    return [{"key": k, "kind": "phenotype", "group": g, "probability": round(float(p), 6), "fraction": frac_str(p)}
            for (g, k), p in sorted(totals.items(), key=lambda kv: -kv[1]) if p > 0]


def _limitations(disease, statuses):
    limitations = list(disease.get("limitations", []))
    if "non_carrier" in statuses:
        limitations.append("negative_test_residual")
    return limitations


def carrier_analysis(disease_id: str, mother_status: str, father_status: str, region: str | None = None,
                     diseases: dict | None = None) -> dict:
    diseases = diseases or load_diseases()
    disease, ar, m_options, f_options = _resolve(disease_id, mother_status, father_status, diseases)
    statuses = (mother_status, father_status)
    scenarios = [{"mother_genotype": m, "father_genotype": f, "outcomes": _run_cross(disease, ar, m, f)}
                 for m, f in product(m_options, f_options)]
    inputs = {"disease_id": disease_id, "mother_status": mother_status, "father_status": father_status,
              "region": region}
    assumptions = ["stated_status_correct", "mendelian_segregation", "complete_penetrance"]
    limitations = _limitations(disease, statuses)
    refs, data_version = disease["references"], diseases.get("_version")
    common = {"disease": disease_id, "inheritance": disease["inheritance"], "scenarios": scenarios}

    if "unknown" not in statuses:
        return make_result("carrier_risk", "established", "carrier_exact", inputs, scenarios[0]["outcomes"],
                           assumptions, limitations, refs, common, data_version)

    assumptions.append("unknown_parent_unaffected")
    entry = _validated_region(disease, region) if region else None
    if entry is None:
        common["population_estimate"] = {"available": False, "reason": "region_data_unvalidated"}
        return make_result("carrier_risk", "established", "carrier_conditional", inputs, [],
                           assumptions, [*limitations, "region_data_unvalidated"], refs, common, data_version)

    common["population_estimate"] = {"available": True, "region": region, "source": entry["source"]}
    return make_result("carrier_risk", "population_estimate", "carrier_population", inputs,
                       _population_outcomes(scenarios, statuses, entry, ar),
                       [*assumptions, "regional_frequency_applies"], limitations, [*refs, entry["source"]],
                       common, data_version)
