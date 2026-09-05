from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.match import Match
from app.models.message import Message
from app.models.photo import Photo
from app.models.swipe import Swipe, SwipeAction
from app.models.user import User
from app.schemas.match import LikedMeOut, MatchOut

router = APIRouter(prefix="/matches", tags=["matches"])


def _primary_photo(user: User) -> Photo | None:
    for photo in user.photos:
        if photo.is_primary:
            return photo
    return user.photos[0] if user.photos else None


@router.get("", response_model=list[MatchOut])
def list_matches(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    matches = (
        db.query(Match)
        .filter(or_(Match.user_a_id == current_user.id, Match.user_b_id == current_user.id))
        .order_by(Match.created_at.desc())
        .all()
    )

    results = []
    for match in matches:
        other_id = match.user_b_id if match.user_a_id == current_user.id else match.user_a_id
        other_user = (
            db.query(User).options(selectinload(User.photos)).filter(User.id == other_id).first()
        )
        last_message = (
            db.query(Message).filter(Message.match_id == match.id).order_by(Message.created_at.desc()).first()
        )
        results.append(
            MatchOut(
                match_id=match.id,
                user_id=other_user.id,
                name=other_user.name,
                primary_photo=_primary_photo(other_user),
                created_at=match.created_at,
                last_message=last_message.content if last_message else None,
                last_message_at=last_message.created_at if last_message else None,
            )
        )
    return results


@router.get("/liked-me", response_model=list[LikedMeOut])
def liked_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    matched_ids = {
        (m.user_a_id if m.user_b_id == current_user.id else m.user_b_id)
        for m in db.query(Match).filter(or_(Match.user_a_id == current_user.id, Match.user_b_id == current_user.id)).all()
    }

    likers = (
        db.query(Swipe)
        .filter(Swipe.target_id == current_user.id, Swipe.action == SwipeAction.like)
        .order_by(Swipe.created_at.desc())
        .all()
    )

    results = []
    for like in likers:
        if like.swiper_id in matched_ids:
            continue
        liker = db.query(User).options(selectinload(User.photos)).filter(User.id == like.swiper_id).first()
        if liker is None:
            continue
        results.append(
            LikedMeOut(
                user_id=liker.id,
                name=liker.name,
                primary_photo=_primary_photo(liker),
                liked_at=like.created_at,
            )
        )
    return results
