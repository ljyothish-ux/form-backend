from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class Form(Base):
    __tablename__ = "forms"

    id         = Column(Integer, primary_key=True, index=True)
    title      = Column(String, nullable=False)
    description= Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())