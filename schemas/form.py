from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FormCreate(BaseModel):
    title:         str
    description:   Optional[str] = None
    location:      Optional[str] = None
    timer_seconds: Optional[int] = None   # ← new
    is_active:     Optional[bool] = True  # ← new


class FormUpdate(BaseModel):              # ← new — for PUT /forms/{id}
    title:         Optional[str]  = None
    description:   Optional[str]  = None
    location:      Optional[str]  = None
    timer_seconds: Optional[int]  = None
    is_active:     Optional[bool] = None


class FormResponse(BaseModel):
    id:            int
    title:         str
    description:   Optional[str]  = None
    location:      Optional[str]  = None
    timer_seconds: Optional[int]  = None  # ← new
    is_active:     bool                   # ← new
    created_at:    datetime

    class Config:
        from_attributes = True