"""What ordinary users may see of a family-pattern result. The table, matching and details stay server-side."""
from .i18n import t
from .traditional.family_pattern import load_table

PROTECTED_KIND = "family-pattern"
DAILY_LIMIT = 20


def report_id(analysis_id: str) -> str:
    return f"GN-{analysis_id[-8:].upper()}"


def stated_range(outcome: dict) -> str | None:
    """Engine-provided percentage; older saved results fall back to the PDF header ranges for 3 + 3 families."""
    if "stated_range" in outcome:
        return outcome["stated_range"]
    group = outcome["group"]
    return load_table()["pdf_stated_ranges"].get(group) if group in ("first_child", "second_child") else None


def _public_result(r: dict) -> dict:
    lang = r["lang"]
    outcomes = [{"key": o["key"], "label": o["label"], "group": o["group"], "group_label": o["group_label"],
                 "kind": "traditional", "probability": None, "fraction": None,
                 "stated_range": stated_range(o)} for o in r["outcomes"]]
    notes = ["traditional_public_disclaimer", *([] if outcomes else ["no_result_available"])]
    return {"analysis_type": "family_pattern", "public": True, "lang": lang, "certainty": r["certainty"],
            "certainty_label": r["certainty_label"], "method": "genova_traditional",
            "method_label": t("genova_traditional", lang), "outcomes": outcomes, "assumptions": [],
            "limitations": [{"key": k, "text": t(k, lang)} for k in notes], "references": [], "details": {},
            "inputs": {}}


def protect_view(view: dict, role: str) -> dict:
    view["report_id"] = report_id(view["id"])
    if view["analysis_type"] != PROTECTED_KIND:
        return view
    if role == "admin":
        for o in view["result"]["outcomes"]:
            o["stated_range"] = stated_range(o)
        return view
    return {**view, "request": {}, "result": _public_result(view["result"])}


def protect_item(item: dict, role: str, lang: str) -> dict:
    if item["analysis_type"] != PROTECTED_KIND or role == "admin":
        return item
    return {**item, "request": {}, "method_label": t("genova_traditional", lang)}
