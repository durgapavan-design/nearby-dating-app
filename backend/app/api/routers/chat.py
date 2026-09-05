import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import decode_access_token
from app.db.session import SessionLocal, get_db
from app.models.match import Match
from app.models.message import Message
from app.models.user import User
from app.schemas.message import MessageIn, MessageOut
from app.services.ws_manager import manager

router = APIRouter(tags=["chat"])


def _get_match_for_user(db: Session, match_id: uuid.UUID, user_id: uuid.UUID) -> Match:
    match = db.query(Match).filter(Match.id == match_id).first()
    if match is None or user_id not in (match.user_a_id, match.user_b_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return match


@router.get("/matches/{match_id}/messages", response_model=list[MessageOut])
def get_messages(
    match_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_match_for_user(db, match_id, current_user.id)
    return (
        db.query(Message)
        .filter(Message.match_id == match_id)
        .order_by(Message.created_at.asc())
        .all()
    )


@router.post("/matches/{match_id}/messages", response_model=MessageOut)
async def post_message(
    match_id: uuid.UUID,
    payload: MessageIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_match_for_user(db, match_id, current_user.id)
    message = Message(match_id=match_id, sender_id=current_user.id, content=payload.content)
    db.add(message)
    db.commit()
    db.refresh(message)

    out = MessageOut.model_validate(message, from_attributes=True)
    await manager.broadcast(match_id, out.model_dump(mode="json"))
    return out


@router.websocket("/ws/chat/{match_id}")
async def chat_websocket(websocket: WebSocket, match_id: uuid.UUID, token: str = Query(...)):
    user_id = decode_access_token(token)
    if user_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    db = SessionLocal()
    try:
        match = db.query(Match).filter(Match.id == match_id).first()
        if match is None or user_id not in (match.user_a_id, match.user_b_id):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    finally:
        db.close()

    await manager.connect(match_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            content = (data.get("content") or "").strip()
            if not content:
                continue

            db = SessionLocal()
            try:
                message = Message(match_id=match_id, sender_id=user_id, content=content)
                db.add(message)
                db.commit()
                db.refresh(message)
                out = MessageOut.model_validate(message, from_attributes=True)
            finally:
                db.close()

            await manager.broadcast(match_id, out.model_dump(mode="json"))
    except WebSocketDisconnect:
        manager.disconnect(match_id, websocket)
