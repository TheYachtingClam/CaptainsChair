from fastapi import APIRouter, Depends

from app import content
from app.auth import require_session

router = APIRouter(prefix="/api/content", tags=["content"], dependencies=[Depends(require_session)])


@router.get("/decks")
def list_decks() -> list[dict]:
    return content.decks()


@router.get("/expansions")
def list_expansions() -> dict[str, str]:
    return content.EXPANSIONS
