from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Scan(Base):
    __tablename__ = "scans"

    id                 = Column(Integer, primary_key=True, index=True)
    form_id            = Column(Integer, ForeignKey("forms.id"), nullable=False)
    user_id            = Column(Integer, ForeignKey("users.id"), nullable=True)  # null until OTP done
    latitude           = Column(Float, nullable=True)    # null if user denies GPS
    longitude          = Column(Float, nullable=True)    # null if user denies GPS
    device_fingerprint = Column(String, nullable=True)   # hash of browser signals
    user_agent         = Column(String, nullable=True)   # browser/device string
    ip_address         = Column(String, nullable=True)   # captured from request
    scanned_at         = Column(DateTime(timezone=True), server_default=func.now())