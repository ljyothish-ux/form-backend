from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.otp_verification import OTPVerification
from schemas.user import UserIdentify, UserResponse, UserCheckResponse
from typing import List

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/identify", response_model=UserResponse)
def identify_user(user_data: UserIdentify, db: Session = Depends(get_db)):

    name  = user_data.name.strip()
    phone = user_data.phone.strip()

    if not name:
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    if not phone:
        raise HTTPException(status_code=400, detail="Phone cannot be empty")
    if not phone.isdigit():
        raise HTTPException(status_code=400, detail="Phone must contain digits only")
    if not (7 <= len(phone) <= 15):
        raise HTTPException(status_code=400, detail="Phone must be between 7 and 15 digits")

    # Check if OTP was verified for this phone
    otp_verified = (
        db.query(OTPVerification)
        .filter(
            OTPVerification.phone   == phone,
            OTPVerification.is_used == True      # ← is_used=True means verified
        )
        .first()
    )

    # Check if user already exists
    existing_user = db.query(User).filter(User.phone == phone).first()

    if existing_user:
        # Update is_verified if OTP was done
        if otp_verified and not existing_user.is_verified:
            existing_user.is_verified = True
            db.commit()
            db.refresh(existing_user)
        return existing_user

    # New user — create them
    new_user = User(
        name=name,
        phone=phone,
        is_verified=True if otp_verified else False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ─────────────────────────────────────────
# GET /users/check/{phone}
# Frontend calls this first on QR scan
# Returns exists: true/false
# ─────────────────────────────────────────
@router.get("/check/{phone}", response_model=UserCheckResponse)
def check_user(phone: str, db: Session = Depends(get_db)):

    phone = phone.strip()

    user = db.query(User).filter(User.phone == phone).first()

    if user:
        return {
            "exists": True,
            "user": user
        }

    return {
        "exists": False,
        "user": None
    }


# ─────────────────────────────────────────
# GET /users/{user_id}
# Get a specific user by ID
# ─────────────────────────────────────────
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# ─────────────────────────────────────────
# GET /users
# List all users (admin use)
# ─────────────────────────────────────────
@router.get("/", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users