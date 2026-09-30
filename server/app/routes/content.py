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
def list_images(kind: str | None = None) -> dict[str, dict]:
    """Every processed image: id -> {url, kind, width, height}. Filter with ?kind=cards|boards|command.

    Game views must only include an image URL for cards the viewing player may see;
    facedown cards use a card-back id instead (REQ-SRV-20).
    """
    return {
        image_id: {
            "url": content.image_url(image_id),
            "kind": entry["kind"],
            "width": entry["width"],
            "height": entry["height"],
        }
        for image_id, entry in content.image_manifest().items()
        if kind is None or entry["kind"] == kind
    }


@router.get("/images/{image_id}")
def image(image_id: str, v: str | None = None) -> FileResponse:
    path = content.image_path(image_id)
    if path is None:
        raise HTTPException(404, "No such image")
    version = content.image_manifest()[image_id]["version"]
    # A URL with the current version never changes, so it can be cached for a year.
    # "private" keeps shared caches from storing images that sit behind the site password.
    cache = "private, max-age=31536000, immutable" if v == version else "private, no-cache"
    return FileResponse(path, media_type="image/webp", headers={"Cache-Control": cache})
