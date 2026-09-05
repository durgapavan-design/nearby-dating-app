from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import OtpRequest, OtpRequestResponse, OtpVerify, TokenResponse
from app.services.otp_service import generate_and_store_otp, verify_otp

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/otp/request", response_model=OtpRequestResponse)
def request_otp(payload: OtpRequest, db: Session = Depends(get_db)):
    code = generate_and_store_otp(db, payload.phone_number)
    return OtpRequestResponse(
        message="OTP generated (dev mode: no real SMS sent).",
        debug_code=code if settings.otp_debug_mode else None,
    )


@router.post("/otp/verify", response_model=TokenResponse)
def verify_otp_code(payload: OtpVerify, db: Session = Depends(get_db)):
    from fastapi import HTTPException, status

    if not verify_otp(db, payload.phone_number, payload.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired code")

    user = db.query(User).filter(User.phone_number == payload.phone_number).first()
    is_new_user = user is None
    if user is None:
        user = User(phone_number=payload.phone_number)
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        is_new_user=is_new_user,
        profile_completed=user.profile_completed,
    )
