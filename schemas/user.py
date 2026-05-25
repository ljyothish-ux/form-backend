from pydantic import BaseModel
from datetime import datetime

# What frontend sends to identify a user
class UserIdentify(BaseModel):
    name:  str
    phone: str

# What API sends back
class UserResponse(BaseModel):
    id:         int
    name:       str
    phone:      str
    created_at: datetime

    class Config:
        from_attributes = True

# What API sends back for check endpoint
class UserCheckResponse(BaseModel):
    exists: bool
    user:   UserResponse | None = None