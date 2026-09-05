import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.otp import OtpCode


def generate_and_store_otp(db: Session, phone_number: str) -> str:
    code = f"{random.randint(0, 999999):06d}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.otp_expire_minutes)
    otp = OtpCode(phone_number=phone_number, code=code, expires_at=expires_at)
    db.add(otp)
    db.commit()
    # MVP: no real SMS provider wired up. In debug mode the caller returns this code
    # directly in the API response; a real provider integration would replace this
    # function's return with an actual send-and-forget call.
    return code


def verify_otp(db: Session, phone_number: str, code: str) -> bool:
    now = datetime.now(timezone.utc)
    otp = (
        db.query(OtpCode)
        .filter(
            OtpCode.phone_number == phone_number,
            OtpCode.code == code,
            OtpCode.is_used.is_(False),
            OtpCode.expires_at > now,
        )
        .order_by(OtpCode.created_at.desc())
        .first()
    )
    if otp is None:
        return False

    otp.is_used = True
    db.commit()
    return True
