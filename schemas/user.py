from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserIdentify(BaseModel):
    name:  str
    phone: str


class UserResponse(BaseModel):
    id:          int
    name:        str
    phone:       str
    is_verified: bool        # ← new field
    created_at:  datetime

    class Config:
        from_attributes = True


class UserCheckResponse(BaseModel):
    exists: bool
    user:   Optional[UserResponse] = None