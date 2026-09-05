import uuid

from sqlalchemy.orm import Session

from app.models.swipe import Swipe
from app.models.user import Gender, ShowMe, User

CITY_MATCH_WEIGHT = 10
SHARED_INTEREST_WEIGHT = 2


def compatible_gender(viewer: User, candidate: User) -> bool:
    """Mutual compatibility: candidate must match what viewer wants to see, and vice versa."""
    if viewer.show_me != ShowMe.everyone and candidate.gender is not None:
        if viewer.show_me and viewer.show_me.value != candidate.gender.value:
            return False
    if candidate.show_me and candidate.show_me != ShowMe.everyone and viewer.gender is not None:
        if candidate.show_me.value != viewer.gender.value:
            return False
    return True


def score_candidate(viewer: User, candidate: User) -> int:
    score = 0
    if viewer.city and candidate.city and viewer.city == candidate.city:
        score += CITY_MATCH_WEIGHT
    viewer_interest_ids = {i.id for i in viewer.interests}
    candidate_interest_ids = {i.id for i in candidate.interests}
    shared = len(viewer_interest_ids & candidate_interest_ids)
    score += shared * SHARED_INTEREST_WEIGHT
    return score


def get_discovery_feed(db: Session, viewer: User, limit: int = 20) -> list[tuple[User, int]]:
    swiped_ids = {
        row[0] for row in db.query(Swipe.target_id).filter(Swipe.swiper_id == viewer.id).all()
    }
    swiped_ids.add(viewer.id)

    candidates = (
        db.query(User)
        .filter(User.id.notin_(swiped_ids) if swiped_ids else True, User.is_active.is_(True), User.profile_completed.is_(True))
        .all()
    )

    scored = [
        (c, score_candidate(viewer, c))
        for c in candidates
        if compatible_gender(viewer, c)
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:limit]


def make_match_pair(user_id_a: uuid.UUID, user_id_b: uuid.UUID) -> tuple[uuid.UUID, uuid.UUID]:
    return (user_id_a, user_id_b) if str(user_id_a) < str(user_id_b) else (user_id_b, user_id_a)
