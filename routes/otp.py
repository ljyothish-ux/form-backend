from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import get_db
from models.otp_verification import OTPVerification
from models.user import User
from schemas.otp import OTPSendRequest, OTPSendResponse, OTPVerifyRequest, OTPVerifyResponse
from services.otp_service import generate_otp, hash_otp, verify_otp_hash, send_sms

router = APIRouter(
    prefix="/otp",
    tags=["OTP Verification"]
)

OTP_EXPIRY_MINUTES = 10
OTP_RATE_LIMIT_SECONDS = 60
MAX_ATTEMPTS = 3


# ─────────────────────────────────────────
# POST /otp/send
# Generate and send OTP via SMS
# ─────────────────────────────────────────
@router.post("/send", response_model=OTPSendResponse)
def send_otp(request: OTPSendRequest, db: Session = Depends(get_db)):

    phone = request.phone.strip()

    # Validate phone
    if not phone.isdigit():
        raise HTTPException(status_code=400, detail="Phone must contain digits only")

    if not (7 <= len(phone) <= 15):
        raise HTTPException(status_code=400, detail="Phone must be between 7 and 15 digits")

    # Rate limit — check if OTP was sent in last 60 seconds
    recent_otp = (
        db.query(OTPVerification)
        .filter(OTPVerification.phone == phone)
        .order_by(OTPVerification.created_at.desc())
        .first()
    )

    if recent_otp:
        created = recent_otp.created_at
        if hasattr(created, 'tzinfo') and created.tzinfo is not None:
            created = created.replace(tzinfo=None)
        seconds_since_last = (datetime.utcnow() - created).total_seconds()
        if seconds_since_last < OTP_RATE_LIMIT_SECONDS:
            wait = int(OTP_RATE_LIMIT_SECONDS - seconds_since_last)
            raise HTTPException(
                status_code=429,
                detail=f"Please wait {wait} seconds before requesting another OTP"
            )

    # Generate OTP
    otp_code   = generate_otp()
    otp_hash   = hash_otp(otp_code)
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)

    # Save to DB
    new_otp = OTPVerification(
        phone=phone,
        otp_code=otp_hash,
        expires_at=expires_at
    )
    db.add(new_otp)
    db.commit()

    # Send SMS
    sms_sent = send_sms(phone, otp_code)
    if not sms_sent:
        raise HTTPException(
            status_code=500,
            detail="Failed to send OTP SMS. Please try again."
        )

    return OTPSendResponse(
        message="OTP sent successfully",
        expires_in=OTP_EXPIRY_MINUTES * 60
    )


# ─────────────────────────────────────────
# POST /otp/verify
# Verify OTP entered by user
# ─────────────────────────────────────────
@router.post("/verify", response_model=OTPVerifyResponse)
def verify_otp(request: OTPVerifyRequest, db: Session = Depends(get_db)):

    phone = request.phone.strip()
    otp   = request.otp.strip()

    # Basic input validation
    if not phone or not otp:
        raise HTTPException(status_code=400, detail="Phone and OTP are required")

    # Find the latest unused OTP for this phone
    # Get ALL records for this phone and filter in Python
# This avoids SQLite timezone comparison issues
    all_otps = (
        db.query(OTPVerification)
        .filter(OTPVerification.phone == phone)
        .order_by(OTPVerification.created_at.desc())
        .all()
    )

    # Find the latest unused one
    otp_record = None
    for record in all_otps:
        if not record.is_used:
            otp_record = record
            break

    # No OTP found for this phone
    if not otp_record:
        raise HTTPException(
            status_code=400,
            detail="No OTP found for this phone. Please request a new one."
        )

    # Check if too many wrong attempts
    if otp_record.attempts >= MAX_ATTEMPTS:
        raise HTTPException(
            status_code=400,
            detail="Too many wrong attempts. Please request a new OTP."
        )

    # Check if OTP has expired
    from datetime import timezone
    now = datetime.utcnow()
    expires = otp_record.expires_at
    # Strip timezone info if present to make comparison safe
    if hasattr(expires, 'tzinfo') and expires.tzinfo is not None:
        expires = expires.replace(tzinfo=None)
    if now > expires:
        raise HTTPException(
            status_code=400,
            detail="OTP has expired. Please request a new one."
        )

    # Check if OTP code matches
    if not verify_otp_hash(otp, otp_record.otp_code):
        # Wrong code — increment attempts
        otp_record.attempts += 1
        db.commit()

        remaining = MAX_ATTEMPTS - otp_record.attempts
        raise HTTPException(
            status_code=400,
            detail=f"Incorrect OTP. {remaining} attempt(s) remaining."
        )

    # ✅ OTP is correct — mark as used
    otp_record.is_used = True
    db.commit()

    # Check if user already exists
    existing_user = db.query(User).filter(User.phone == phone).first()

    if existing_user:
        # Mark user as verified
        existing_user.is_verified = True
        db.commit()

        return OTPVerifyResponse(
            verified=True,
            is_new_user=False,
            user_id=existing_user.id,
            message="OTP verified. Welcome back."
        )

    # New user — not in DB yet
    # Frontend will now ask for name and call POST /users/identify
    return OTPVerifyResponse(
        verified=True,
        is_new_user=True,
        user_id=None,
        message="OTP verified. Please enter your name to continue."
    )