from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# POST /otp/send — what frontend sends
class OTPSendRequest(BaseModel):
    phone: str


# POST /otp/send — what API returns
class OTPSendResponse(BaseModel):
    message:    str
    expires_in: int    # seconds until expiry — always 600 (10 mins)


# POST /otp/verify — what frontend sends
class OTPVerifyRequest(BaseModel):
    phone: str
    otp:   str


# POST /otp/verify — what API returns
class OTPVerifyResponse(BaseModel):
    verified:    bool
    is_new_user: bool
    user_id:     Optional[int] = None
    message:     str