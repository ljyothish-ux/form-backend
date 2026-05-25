from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class Question(Base):
    __tablename__ = "questions"

    id            = Column(Integer, primary_key=True, index=True)
    form_id       = Column(Integer, ForeignKey("forms.id"), nullable=False)
    question_text = Column(String, nullable=False)
    question_type = Column(String, nullable=False)  # text, radio, dropdown, rating, checkbox
    options       = Column(String, nullable=True)   # stored as "Option A|Option B|Option C"
    order         = Column(Integer, nullable=False, default=0)