from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models.question import Question
from models.form import Form
from schemas.question import QuestionResponse
from services.csv_parser import parse_csv
from typing import List

router = APIRouter(
    prefix="/forms",
    tags=["Questions"]
)

# ─────────────────────────────────────────
# POST /forms/{form_id}/upload-csv
# Upload a CSV and save questions to DB
# ─────────────────────────────────────────
@router.post("/{form_id}/upload-csv")
async def upload_csv(
    form_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Check form exists
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    # Check file is a CSV
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are allowed")

    # Read file bytes
    file_bytes = await file.read()

    # Parse CSV using our service
    try:
        questions = parse_csv(file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Delete old questions for this form first
    # This means re-uploading a CSV replaces questions, not duplicates them
    db.query(Question).filter(Question.form_id == form_id).delete()
    db.commit()

    # Save new questions
    for q in questions:
        new_question = Question(
            form_id=form_id,
            question_text=q["question_text"],
            question_type=q["question_type"],
            options=q["options"],
            order=q["order"]
        )
        db.add(new_question)

    db.commit()

    return {
        "message": f"Successfully uploaded {len(questions)} questions to form {form_id}",
        "total_questions": len(questions)
    }


# ─────────────────────────────────────────
# GET /forms/{form_id}/questions
# Get all questions for a form
# ─────────────────────────────────────────
@router.get("/{form_id}/questions", response_model=List[QuestionResponse])
def get_questions(form_id: int, db: Session = Depends(get_db)):
    # Check form exists
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    questions = (
        db.query(Question)
        .filter(Question.form_id == form_id)
        .order_by(Question.order)
        .all()
    )

    return questions