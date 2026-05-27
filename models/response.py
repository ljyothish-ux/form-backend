from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base

class Response(Base):
    __tablename__ = "responses"

    id           = Column(Integer, primary_key=True, index=True)
    form_id      = Column(Integer, ForeignKey("forms.id"), nullable=False)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id  = Column(Integer, ForeignKey("questions.id"), nullable=False)
    session_id   = Column(Integer, ForeignKey("form_sessions.id"), nullable=True)  # ← new
    answer       = Column(String, nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())