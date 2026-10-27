from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.auth import websocket_user
from app.db import get_db
from app.hub import hub
from app.routes.games import load_game, seat_for

router = APIRouter()


@router.websocket("/api/games/{game_id}/ws")
async def game_socket(websocket: WebSocket, game_id: str, db: Session = Depends(get_db)) -> None:
    # The signed-in account's seat in this game, checked before accepting (REQ-USER-13, REQ-SRV-40).
    user_id = websocket_user(websocket)
    if user_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Not signed in")
        return
    try:
        game = load_game(db, game_id)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Game not found")
        return
    seat_row = seat_for(game, user_id)
    if seat_row is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="No seat in this game")
        return

    seat_index = seat_row.index
    await websocket.accept()
    await websocket.send_json({"type": "hello", "your_seat": seat_index})
    await hub.connect(game_id, seat_index, websocket)
    try:
        while True:
            message = await websocket.receive_json()
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            else:
                await websocket.send_json({"type": "error", "message": "Gameplay is not implemented yet"})
    except WebSocketDisconnect:
        pass
    finally:
        await hub.disconnect(game_id, seat_index, websocket)
