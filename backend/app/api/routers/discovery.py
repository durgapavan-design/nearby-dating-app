from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.match import Match
from app.models.swipe import Swipe, SwipeAction
from app.models.user import User
from app.schemas.discovery import SwipeIn, SwipeResult
from app.schemas.user import DiscoveryProfileOut
from app.services.matching import get_discovery_feed, make_match_pair

router = APIRouter(prefix="/discovery", tags=["discovery"])


def _age_from_birthdate(birthdate: date | None) -> int | None:
    if birthdate is None:
        return None
    today = date.today()
    years = today.year - birthdate.year
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        years -= 1
    return years


@router.get("/feed", response_model=list[DiscoveryProfileOut])
def get_feed(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    scored = get_discovery_feed(db, current_user)
    viewer_interest_ids = {i.id for i in current_user.interests}

    results = []
    for candidate, _score in scored:
        shared = len(viewer_interest_ids & {i.id for i in candidate.interests})
        results.append(
            DiscoveryProfileOut(
                id=candidate.id,
                name=candidate.name,
                age=_age_from_birthdate(candidate.birthdate),
                bio=candidate.bio,
                city=candidate.city,
                photos=candidate.photos,
                interests=candidate.interests,
                shared_interest_count=shared,
            )
        )
    return results


@router.post("/swipe", response_model=SwipeResult)
def swipe(payload: SwipeIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = (
        db.query(Swipe)
        .filter(Swipe.swiper_id == current_user.id, Swipe.target_id == payload.target_id)
        .first()
    )
    if existing is not None:
        existing.action = payload.action
    else:
        db.add(Swipe(swiper_id=current_user.id, target_id=payload.target_id, action=payload.action))
    db.commit()

    if payload.action != SwipeAction.like:
        return SwipeResult(matched=False)

    reverse_like = (
        db.query(Swipe)
        .filter(
            Swipe.swiper_id == payload.target_id,
            Swipe.target_id == current_user.id,
            Swipe.action == SwipeAction.like,
        )
        .first()
    )
    if reverse_like is None:
        return SwipeResult(matched=False)

    user_a_id, user_b_id = make_match_pair(current_user.id, payload.target_id)
    match = db.query(Match).filter(Match.user_a_id == user_a_id, Match.user_b_id == user_b_id).first()
    if match is None:
        match = Match(user_a_id=user_a_id, user_b_id=user_b_id)
        db.add(match)
        db.commit()
        db.refresh(match)

    return SwipeResult(matched=True, match_id=match.id)
