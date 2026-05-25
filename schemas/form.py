from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# What frontend sends when CREATING a form
class FormCreate(BaseModel):
    title: str
    description: Optional[str] = None

# What your API sends BACK
class FormResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True  # lets pydantic read SQLAlchemy objects