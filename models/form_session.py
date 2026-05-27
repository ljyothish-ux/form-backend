from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class FormSession(Base):
    __tablename__ = "form_sessions"

    id                 = Column(Integer, primary_key=True, index=True)
    form_id            = Column(Integer, ForeignKey("forms.id"), nullable=False)
    user_id            = Column(Integer, ForeignKey("users.id"), nullable=False)
    scan_id            = Column(Integer, ForeignKey("scans.id"), nullable=True)
    started_at         = Column(DateTime(timezone=True), server_default=func.now())
    submitted_at       = Column(DateTime(timezone=True), nullable=True)
    time_taken_seconds = Column(Integer, nullable=True)
    is_completed       = Column(Boolean, default=False)
    is_timed_out       = Column(Boolean, default=False)