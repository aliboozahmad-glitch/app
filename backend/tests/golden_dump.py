"""Dump deterministic outputs of blood_type_analysis, carrier_analysis and localize_result for a full input matrix.
Usage: python golden_dump.py <backend_root>  -> prints JSON. Used to compare refactored code against a previous commit."""
import itertools
import json
import sys

sys.path.insert(0, sys.argv[1])
from genova.genetics.blood_type import blood_type_analysis  # noqa: E402
from genova.genetics.carrier_risk import carrier_analysis  # noqa: E402
from genova.genetics.data_loader import load_diseases  # noqa: E402
from genova.i18n import localize_result  # noqa: E402


def safe(fn, *a):
    try:
        return fn(*a)
    except Exception as e:  # noqa: BLE001
        return {"error": type(e).__name__, "msg": str(e)}


out = {}
ABO = ["A", "B", "AB", "O", "AA", "AO", "BB", "BO", "OO", "unknown", "X"]
RH = ["+", "-", "DD", "Dd", "dd", "unknown", "?"]
for p1a, p1r, p2a, p2r in itertools.product(["A", "B", "AB", "O", "AO", "unknown"], ["+", "-", "Dd", "unknown"],
                                            ABO, RH):
    k = f"blood|{p1a}|{p1r}|{p2a}|{p2r}"
    r = safe(blood_type_analysis, p1a, p1r, p2a, p2r)
    out[k] = r
    if "error" not in r:
        for lang in ("en", "ar", "de"):
            out[k + "|" + lang] = safe(localize_result, r, lang)

diseases = load_diseases()
statuses = ["affected", "carrier", "non_carrier", "unaffected", "unknown", "bogus"]
regions = [None, "gulf", "saudi", "levant", "europe", "global", "bogus"]
for did in list(diseases) + ["nope"]:
    for m, f, reg in itertools.product(statuses, statuses, regions):
        k = f"carrier|{did}|{m}|{f}|{reg}"
        r = safe(carrier_analysis, did, m, f, reg)
        out[k] = r
        if "error" not in r:
            for lang in ("en", "ar", "de"):
                out[k + "|" + lang] = safe(localize_result, r, lang)

print(json.dumps(out, sort_keys=True, default=str))
