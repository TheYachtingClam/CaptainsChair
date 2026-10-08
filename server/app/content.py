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


def bot_ids_for(expansions: list[str]) -> set[str]:
    """Crews that can be the Bot in solo mode: they have Automated Command cards and their Bot is written."""
    from engine.content import content
    from engine.setup import BOT_UNAVAILABLE

    return {d for d in deck_ids_for(expansions) if d in content().command and d not in BOT_UNAVAILABLE}


# Processed images (cards, crew boards, command cards), produced by scripts/process_scans.py.
IMAGES_DIR = CONTENT_DIR / "images"
_manifest_cache: tuple[float, dict[str, dict]] | None = None


def image_manifest() -> dict[str, dict]:
    """Image id -> {"kind", "file", "width", "height", "version", ...}.

    Reloaded whenever manifest.json changes.
    """
    global _manifest_cache
    path = IMAGES_DIR / "manifest.json"
    if not path.exists():
        return {}
    mtime = path.stat().st_mtime
    if _manifest_cache is None or _manifest_cache[0] != mtime:
        _manifest_cache = (mtime, json.loads(path.read_text()).get("images", {}))
    return _manifest_cache[1]


def image_url(image_id: str) -> str | None:
    """Versioned URL for an image, so browsers can cache it for good."""
    entry = image_manifest().get(image_id)
    return f"/api/content/images/{image_id}?v={entry['version']}" if entry else None


def image_path(image_id: str) -> Path | None:
    entry = image_manifest().get(image_id)
    if not entry:
        return None
    root = IMAGES_DIR.resolve()
    path = (root / entry["file"]).resolve()
    # The manifest is trusted build output, but never serve anything outside the images folder.
    if root not in path.parents or not path.is_file():
        return None
    return path
