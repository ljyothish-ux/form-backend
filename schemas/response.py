from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# One single answer to one question
class AnswerItem(BaseModel):
    question_id: int
    answer:      str


# What frontend sends when submitting the form
class SubmitResponse(BaseModel):
    user_id:  int
    session_id: Optional[int] = None
    answers:  List[AnswerItem]


# What API sends back for one response row
class ResponseOut(BaseModel):
    id:           int
    form_id:      int
    user_id:      int
    question_id:  int
    answer:       Optional[str] = None
    submitted_at: datetime

    class Config:
        from_attributes = True


# For the export — one row per user with all their answers
class ResponseExportRow(BaseModel):
    user_id:      int
    user_name:    str
    user_phone:   str
    question:     str
    answer:       Optional[str] = None
    submitted_at: datetime