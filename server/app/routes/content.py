from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app import content
from app.auth import require_session

router = APIRouter(prefix="/api/content", tags=["content"], dependencies=[Depends(require_session)])


@router.get("/decks")
def list_decks() -> list[dict]:
    return content.decks()


@router.get("/expansions")
def list_expansions() -> dict[str, str]:
    return content.EXPANSIONS


@router.get("/images")
def list_images() -> dict[str, str]:
    """Card id -> versioned image URL for every processed card image.

    Game views must only include an image URL for cards the viewing player may see;
    facedown cards use a card-back id instead (REQ-SRV-20).
    """
    return {card_id: content.image_url(card_id) for card_id in content.image_manifest()}


@router.get("/cards/{card_id}/image")
def card_image(card_id: str, v: str | None = None) -> FileResponse:
    path = content.image_path(card_id)
    if path is None:
        raise HTTPException(404, "No image for that card")
    version = content.image_manifest()[card_id]["version"]
    # A URL with the current version never changes, so it can be cached for a year.
    # "private" keeps shared caches from storing images that sit behind the site password.
    cache = "private, max-age=31536000, immutable" if v == version else "private, no-cache"
    return FileResponse(path, media_type="image/webp", headers={"Cache-Control": cache})
