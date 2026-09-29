"""Tracks live WebSocket connections per game (REQ-SRV-40 to REQ-SRV-44)."""

import asyncio
from collections import defaultdict

from fastapi import WebSocket


class GameHub:
    def __init__(self) -> None:
        self._connections: dict[str, dict[int, set[WebSocket]]] = defaultdict(lambda: defaultdict(set))
        self._lock = asyncio.Lock()

    async def connect(self, game_id: str, seat: int, ws: WebSocket) -> None:
        async with self._lock:
            self._connections[game_id][seat].add(ws)
        await self.broadcast_presence(game_id)

    async def disconnect(self, game_id: str, seat: int, ws: WebSocket) -> None:
        async with self._lock:
            seats = self._connections.get(game_id)
            if seats is not None:
                seats[seat].discard(ws)
                if not seats[seat]:
                    del seats[seat]
                if not seats:
                    del self._connections[game_id]
        await self.broadcast_presence(game_id)

    def connected_seats(self, game_id: str) -> list[int]:
        return sorted(self._connections.get(game_id, {}).keys())

    async def broadcast_presence(self, game_id: str) -> None:
        await self.broadcast(game_id, {"type": "presence", "connected": self.connected_seats(game_id)})

    async def broadcast(self, game_id: str, message: dict) -> None:
        sockets = [ws for conns in self._connections.get(game_id, {}).values() for ws in conns]
        for ws in sockets:
            try:
                await ws.send_json(message)
            except Exception:  # a closed socket is cleaned up by its own handler
                pass


hub = GameHub()
