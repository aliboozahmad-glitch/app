"""Anonymous prediction log for the admin statistics; survives history deletion. No user ids are stored."""
from .db import db
from .protection import PROTECTED_KIND, stated_range


def method_group(result: dict) -> str:
    if result.get("details", {}).get("answer_borrowed"):
        return "other_case_answer"
    inp = result.get("inputs", {})
    two = len(inp.get("wife", [])) == 3 and len(inp.get("husband", [])) == 3
    return "two_child_table" if two else "one_child_table"


def snapshot(result: dict) -> dict:
    outcome = result["outcomes"][0]
    return {"predicted": outcome["key"], "stated_range": stated_range(outcome),
            "method_group": method_group(result), "data_version": result.get("data_version")}


async def log_prediction(analysis_id: str, kind: str, result: dict, created_at) -> None:
    if kind != PROTECTED_KIND or not result.get("outcomes"):
        return
    await db.prediction_log.update_one({"analysis_id": analysis_id},
                                       {"$setOnInsert": {**snapshot(result), "created_at": created_at}}, upsert=True)


async def backfill_prediction_log() -> None:
    logged = set(await db.prediction_log.distinct("analysis_id"))
    cursor = db.analyses.find({"analysis_type": PROTECTED_KIND, "result.outcomes.0": {"$exists": True}},
                              {"result": 1, "created_at": 1})
    async for raw in cursor:
        if str(raw["_id"]) not in logged:
            await log_prediction(str(raw["_id"]), PROTECTED_KIND, raw["result"], raw.get("created_at"))
