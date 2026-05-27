from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FormCreate(BaseModel):
    title:       str
    description: Optional[str] = None
    location:    Optional[str] = None    # ← new


class FormResponse(BaseModel):
    id:          int
    title:       str
    description: Optional[str] = None
    location:    Optional[str] = None    # ← new
    created_at:  datetime

    class Config:
        from_attributes = True