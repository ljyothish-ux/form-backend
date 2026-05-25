from pydantic import BaseModel
from typing import Optional

class QuestionResponse(BaseModel):
    id:            int
    form_id:       int
    question_text: str
    question_type: str
    options:       Optional[str] = None
    order:         int

    class Config:
        from_attributes = True