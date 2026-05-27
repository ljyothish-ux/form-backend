from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

class Form(Base):
    __tablename__ = "forms"

    id             = Column(Integer, primary_key=True, index=True)
    title          = Column(String, nullable=False)
    description    = Column(String, nullable=True)
    location       = Column(String, nullable=True)
    timer_seconds  = Column(Integer, nullable=True)   # ← new — null means no timer
    is_active      = Column(Boolean, default=True)    # ← new — active/inactive toggle
    created_at     = Column(DateTime(timezone=True), server_default=func.now())