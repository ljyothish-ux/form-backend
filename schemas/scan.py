from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# What frontend sends when QR is scanned
class ScanCreate(BaseModel):
    form_id:            int
    latitude:           Optional[float] = None
    longitude:          Optional[float] = None
    device_fingerprint: Optional[str]   = None
    user_agent:         Optional[str]   = None


# What API sends back after recording scan
class ScanResponse(BaseModel):
    id:                 int
    form_id:            int
    user_id:            Optional[int]   = None
    latitude:           Optional[float] = None
    longitude:          Optional[float] = None
    device_fingerprint: Optional[str]   = None
    user_agent:         Optional[str]   = None
    ip_address:         Optional[str]   = None
    scanned_at:         datetime

    class Config:
        from_attributes = True


# What frontend sends to link scan to user
class ScanLinkUser(BaseModel):
    user_id: int