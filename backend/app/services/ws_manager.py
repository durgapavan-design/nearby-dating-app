import uuid

from fastapi import WebSocket


class ChatConnectionManager:
    """One socket group per match_id. MVP scope: a single-process server, in-memory only."""

    def __init__(self) -> None:
        self._rooms: dict[uuid.UUID, list[WebSocket]] = {}

    async def connect(self, match_id: uuid.UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self._rooms.setdefault(match_id, []).append(websocket)

    def disconnect(self, match_id: uuid.UUID, websocket: WebSocket) -> None:
        connections = self._rooms.get(match_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections and match_id in self._rooms:
            del self._rooms[match_id]

    async def broadcast(self, match_id: uuid.UUID, message: dict) -> None:
        for connection in self._rooms.get(match_id, []):
            await connection.send_json(message)


manager = ChatConnectionManager()
