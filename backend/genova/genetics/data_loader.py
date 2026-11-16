import json
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


@lru_cache(maxsize=1)
def load_diseases() -> dict:
    raw = json.loads((DATA_DIR / "diseases.json").read_text(encoding="utf-8"))
    out = {d["id"]: d for d in raw["diseases"]}
    out["_version"] = raw["version"]
    return out


@lru_cache(maxsize=1)
def load_references() -> dict:
    raw = json.loads((DATA_DIR / "references.json").read_text(encoding="utf-8"))
    return {r["id"]: r for r in raw["references"]}


def disease_list() -> list:
    return [d for k, d in load_diseases().items() if not k.startswith("_")]
