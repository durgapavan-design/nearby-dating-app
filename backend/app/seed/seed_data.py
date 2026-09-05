"""One-off local seed script. Run with: python -m app.seed.seed_data

Populates ~150 fake profiles (interests, photos, a bit of like/pass activity)
so the discovery feed, matches, and chat screens have data to demo against.
Safe to re-run: skips work if users already exist.
"""
import random
from datetime import date, timedelta

import httpx
from faker import Faker

from app.db.session import Base, SessionLocal, engine
from app.models.interest import Interest
from app.models.photo import Photo
from app.models.swipe import Swipe, SwipeAction
from app.models.user import Gender, ShowMe, User
from app.seed.cities import CITIES
from app.seed.interests_data import INTERESTS

fake = Faker()
NUM_USERS = 150
GENDER_CHOICES = [Gender.male, Gender.female, Gender.non_binary, Gender.other]
SHOW_ME_CHOICES = [ShowMe.male, ShowMe.female, ShowMe.everyone]


def _name_for_gender(gender: Gender) -> str:
    if gender == Gender.male:
        return fake.first_name_male()
    if gender == Gender.female:
        return fake.first_name_female()
    return fake.first_name()


def _random_birthdate() -> date:
    age_days = random.randint(18 * 365, 45 * 365)
    return date.today() - timedelta(days=age_days)


def _seed_interests(db) -> list[Interest]:
    existing = db.query(Interest).count()
    if existing == 0:
        db.add_all(Interest(name=name, category=category) for name, category in INTERESTS)
        db.commit()
    return db.query(Interest).all()


def _download_avatar(gender: Gender, index: int) -> bytes | None:
    if gender == Gender.female:
        pool = "women"
    elif gender == Gender.male:
        pool = "men"
    else:
        pool = random.choice(["men", "women"])
    url = f"https://randomuser.me/api/portraits/{pool}/{index % 99}.jpg"
    try:
        resp = httpx.get(url, timeout=5)
        if resp.status_code == 200:
            return resp.content
    except httpx.HTTPError:
        pass
    return None


def seed():
    Base.metadata.create_all(bind=engine)  # no-op once alembic migrations have run; safe fallback
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Users already seeded, skipping.")
            return

        interests = _seed_interests(db)

        for i in range(NUM_USERS):
            gender = random.choice(GENDER_CHOICES)
            user = User(
                phone_number=f"+91{9000000000 + i}",
                name=_name_for_gender(gender),
                birthdate=_random_birthdate(),
                gender=gender,
                show_me=random.choice(SHOW_ME_CHOICES),
                bio=fake.sentence(nb_words=12),
                city=random.choice(CITIES),
                profile_completed=True,
                interests=random.sample(interests, k=random.randint(2, 6)),
            )
            db.add(user)
            db.flush()  # get user.id before photo insert

            avatar_bytes = _download_avatar(gender, i)
            if avatar_bytes:
                import os

                user_dir = os.path.join("uploads", str(user.id))
                os.makedirs(user_dir, exist_ok=True)
                file_path = os.path.join(user_dir, "seed.jpg")
                with open(file_path, "wb") as f:
                    f.write(avatar_bytes)
                db.add(Photo(user_id=user.id, url=f"/uploads/{user.id}/seed.jpg", position=0, is_primary=True))

            if (i + 1) % 25 == 0:
                print(f"Seeded {i + 1}/{NUM_USERS} users...")

        db.commit()

        all_users = db.query(User).all()
        for user in all_users:
            candidates = random.sample(all_users, k=min(15, len(all_users)))
            for target in candidates:
                if target.id == user.id:
                    continue
                action = SwipeAction.like if random.random() < 0.5 else SwipeAction.pass_
                db.add(Swipe(swiper_id=user.id, target_id=target.id, action=action))
        db.commit()

        print(f"Done. Seeded {NUM_USERS} users with interests, photos, and swipe activity.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
