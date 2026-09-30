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


# Processed card images, produced by scripts/process_scans.py.
IMAGES_DIR = CONTENT_DIR / "images"
_manifest_cache: tuple[float, dict[str, dict]] | None = None


def image_manifest() -> dict[str, dict]:
    """Card id -> {"file", "version", ...}. Reloaded when manifest.json changes."""
    global _manifest_cache
    path = IMAGES_DIR / "manifest.json"
    if not path.exists():
        return {}
    mtime = path.stat().st_mtime
    if _manifest_cache is None or _manifest_cache[0] != mtime:
        _manifest_cache = (mtime, json.loads(path.read_text()).get("cards", {}))
    return _manifest_cache[1]


def image_url(card_id: str) -> str | None:
    """Versioned URL for a card image, so browsers can cache it for good."""
    entry = image_manifest().get(card_id)
    return f"/api/content/cards/{card_id}/image?v={entry['version']}" if entry else None


def image_path(card_id: str) -> Path | None:
    entry = image_manifest().get(card_id)
    if not entry:
        return None
    root = IMAGES_DIR.resolve()
    path = (root / entry["file"]).resolve()
    # The manifest is trusted build output, but never serve anything outside the images folder.
    if root not in path.parents or not path.is_file():
        return None
    return path
