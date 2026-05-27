from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id         = Column(Integer, primary_key=True, index=True)
    phone      = Column(String, nullable=False, index=True)
    otp_code   = Column(String, nullable=False)      # stored as hash
    is_used    = Column(Boolean, default=False)
    attempts   = Column(Integer, default=0)          # wrong attempt counter
    expires_at = Column(DateTime, nullable=False)    # now + 10 minutes
    created_at = Column(DateTime(timezone=True), server_default=func.now())