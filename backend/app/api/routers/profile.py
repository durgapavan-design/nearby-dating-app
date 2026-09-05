import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.interest import Interest
from app.models.photo import Photo
from app.models.user import User
from app.schemas.user import InterestIdsUpdate, InterestOut, MeOut, PhotoOut, ProfileUpdate
from app.seed.cities import CITIES

router = APIRouter(tags=["profile"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


def _load_full_user(db: Session, user_id: uuid.UUID) -> User:
    user = (
        db.query(User)
        .options(selectinload(User.photos), selectinload(User.interests))
        .filter(User.id == user_id)
        .first()
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/me", response_model=MeOut)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _load_full_user(db, current_user.id)


@router.put("/me", response_model=MeOut)
def update_me(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.city is not None and payload.city not in CITIES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown city")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)

    if current_user.name and current_user.birthdate and current_user.gender and current_user.show_me and current_user.city:
        current_user.profile_completed = True

    db.commit()
    return _load_full_user(db, current_user.id)


@router.get("/meta/cities", response_model=list[str])
def list_cities():
    return CITIES


@router.get("/interests", response_model=list[InterestOut])
def list_interests(db: Session = Depends(get_db)):
    return db.query(Interest).order_by(Interest.category, Interest.name).all()


@router.put("/me/interests", response_model=MeOut)
def update_my_interests(
    payload: InterestIdsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    interests = db.query(Interest).filter(Interest.id.in_(payload.interest_ids)).all()
    current_user.interests = interests
    db.commit()
    return _load_full_user(db, current_user.id)


@router.post("/me/photos", response_model=PhotoOut)
async def upload_photo(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported image type")

    existing_count = db.query(Photo).filter(Photo.user_id == current_user.id).count()
    if existing_count >= settings.max_photos_per_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Photo limit reached")

    ext = os.path.splitext(file.filename or "")[1] or ".jpg"
    user_dir = os.path.join(settings.upload_dir, str(current_user.id))
    os.makedirs(user_dir, exist_ok=True)
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(user_dir, filename)

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    photo = Photo(
        user_id=current_user.id,
        url=f"/uploads/{current_user.id}/{filename}",
        position=existing_count,
        is_primary=existing_count == 0,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


@router.delete("/me/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(
    photo_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    photo = db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == current_user.id).first()
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    file_path = os.path.join(settings.upload_dir, str(current_user.id), os.path.basename(photo.url))
    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(photo)
    db.commit()
