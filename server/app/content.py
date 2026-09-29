import json
from functools import lru_cache
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"

BASE_SET = "to_boldly_go"
EXPANSIONS = {"second_contact": "Second Contact"}


@lru_cache
def decks() -> list[dict]:
    return json.loads((CONTENT_DIR / "decks.json").read_text())


def deck_ids_for(expansions: list[str]) -> set[str]:
    allowed = {BASE_SET, *expansions}
    return {d["id"] for d in decks() if d["set"] in allowed}
