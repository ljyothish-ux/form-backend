from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# What frontend sends to start a session
class SessionCreate(BaseModel):
    form_id: int
    user_id: int
    scan_id: Optional[int] = None


# What API sends back — includes timer so frontend knows countdown
class SessionResponse(BaseModel):
    id:                 int
    form_id:            int
    user_id:            int
    scan_id:            Optional[int]      = None
    started_at:         datetime
    submitted_at:       Optional[datetime] = None
    time_taken_seconds: Optional[int]      = None
    is_completed:       bool
    is_timed_out:       bool
    timer_seconds:      Optional[int]      = None  # from form — frontend uses this

    class Config:
        from_attributes = True


# What frontend sends on manual submit
class SessionComplete(BaseModel):
    submitted_at: Optional[datetime] = None  # if not sent backend uses now()