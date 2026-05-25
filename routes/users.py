from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserIdentify, UserResponse, UserCheckResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# ─────────────────────────────────────────
# POST /users/identify
# If phone exists → return existing user
# If phone is new → create and return user
# ─────────────────────────────────────────
@router.post("/identify", response_model=UserResponse)
def identify_user(user_data: UserIdentify, db: Session = Depends(get_db)):

    # Clean inputs — strip spaces
    name  = user_data.name.strip()
    phone = user_data.phone.strip()

    # Validate inputs are not empty
    if not name:
        raise HTTPException(status_code=400, detail="Name cannot be empty")

    if not phone:
        raise HTTPException(status_code=400, detail="Phone cannot be empty")

    # Validate phone — must be digits only, 7 to 15 characters
    if not phone.isdigit():
        raise HTTPException(status_code=400, detail="Phone must contain digits only")

    if not (7 <= len(phone) <= 15):
        raise HTTPException(status_code=400, detail="Phone must be between 7 and 15 digits")

    # Check if user already exists by phone
    existing_user = db.query(User).filter(User.phone == phone).first()

    if existing_user:
        # Return existing user — do NOT create duplicate
        return existing_user

    # New user — create and save
    new_user = User(
        name=name,
        phone=phone
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