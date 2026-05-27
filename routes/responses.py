from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from models.response import Response
from models.form import Form
from models.user import User
from models.question import Question
from schemas.response import SubmitResponse, ResponseOut
from typing import List
import csv
import io

router = APIRouter(
    prefix="/forms",
    tags=["Responses"]
)


# ─────────────────────────────────────────
# POST /forms/{form_id}/responses
# Submit all answers for a form
# ─────────────────────────────────────────
@router.post("/{form_id}/responses")
def submit_responses(
    form_id: int,
    data:    SubmitResponse,
    db:      Session = Depends(get_db)
):
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not data.answers:
        raise HTTPException(status_code=400, detail="No answers provided")

    valid_question_ids = set(
        q.id for q in db.query(Question)
        .filter(Question.form_id == form_id)
        .all()
    )

    for answer_item in data.answers:
        if answer_item.question_id not in valid_question_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Question {answer_item.question_id} does not belong to form {form_id}"
            )

    saved_count = 0
    for answer_item in data.answers:
        new_response = Response(
            form_id=form_id,
            user_id=data.user_id,
            question_id=answer_item.question_id,
            session_id=data.session_id,        # ← new
            answer=answer_item.answer
        )
        db.add(new_response)
        saved_count += 1

    db.commit()

    return {
        "message":      f"Successfully submitted {saved_count} answers",
        "form_id":      form_id,
        "user_id":      data.user_id,
        "session_id":   data.session_id,
        "answers_saved": saved_count
    }

# ─────────────────────────────────────────
# GET /forms/{form_id}/responses
# Get all raw responses for a form (admin)
# ─────────────────────────────────────────
@router.get("/{form_id}/responses", response_model=List[ResponseOut])
def get_responses(
    form_id: int,
    db:      Session = Depends(get_db)
):
    # Check form exists
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    responses = (
        db.query(Response)
        .filter(Response.form_id == form_id)
        .order_by(Response.user_id, Response.question_id)
        .all()
    )

    return responses


# ─────────────────────────────────────────
# GET /forms/{form_id}/responses/export
# Download all responses as a CSV file
# ─────────────────────────────────────────
# @router.get("/{form_id}/responses/export")
# def export_responses(
#     form_id: int,
#     db:      Session = Depends(get_db)
# ):
#     # Check form exists
#     form = db.query(Form).filter(Form.id == form_id).first()
#     if not form:
#         raise HTTPException(status_code=404, detail="Form not found")

#     # Join responses with users and questions to get full picture
#     results = (
#         db.query(
#             Response.id,
#             Response.submitted_at,
#             Response.answer,
#             User.name.label("user_name"),
#             User.phone.label("user_phone"),
#             Question.question_text.label("question")
#         )
#         .join(User,     User.id     == Response.user_id)
#         .join(Question, Question.id == Response.question_id)
#         .filter(Response.form_id == form_id)
#         .order_by(Response.user_id, Question.order)
#         .all()
#     )

#     if not results:
#         raise HTTPException(
#             status_code=404,
#             detail="No responses found for this form"
#         )

#     # Build CSV in memory
#     output = io.StringIO()
#     writer = csv.writer(output)

#     # Header row
#     writer.writerow([
#         "Response ID",
#         "User Name",
#         "User Phone",
#         "Question",
#         "Answer",
#         "Submitted At"
#     ])

#     # Data rows
#     for row in results:
#         writer.writerow([
#             row.id,
#             row.user_name,
#             row.user_phone,
#             row.question,
#             row.answer or "",
#             row.submitted_at
#         ])

#     output.seek(0)

#     # Return as downloadable CSV file
#     return StreamingResponse(
#         io.BytesIO(output.getvalue().encode("utf-8")),
#         media_type="text/csv",
#         headers={
#             "Content-Disposition": f"attachment; filename=form_{form_id}_responses.csv"
#         }
#     )

@router.get("/{form_id}/responses/export")
def export_responses(
    form_id: int,
    db: Session = Depends(get_db)
):
    # Check form exists
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    # Get all questions for this form in order
    questions = (
        db.query(Question)
        .filter(Question.form_id == form_id)
        .order_by(Question.order)
        .all()
    )

    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this form")

    # Get all users who responded to this form
    user_ids = (
        db.query(Response.user_id)
        .filter(Response.form_id == form_id)
        .distinct()
        .all()
    )

    if not user_ids:
        raise HTTPException(status_code=404, detail="No responses found for this form")

    # Build CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # ── Header row ──────────────────────────────────────────
    # Fixed columns first, then one column per question
    header = ["User Name", "User Phone", "Submitted At"]
    for q in questions:
        header.append(q.question_text)
    writer.writerow(header)

    # ── One row per user ─────────────────────────────────────
    for (user_id,) in user_ids:
        user = db.query(User).filter(User.id == user_id).first()

        # Get all answers by this user for this form
        answers = (
            db.query(Response)
            .filter(
                Response.form_id == form_id,
                Response.user_id == user_id
            )
            .all()
        )

        # Map question_id → answer
        answer_map = {a.question_id: a.answer for a in answers}

        # Get submitted_at from first answer
        submitted_at = answers[0].submitted_at if answers else ""

        # Build the row
        # Phone prefixed with = " to force Excel to treat as text
        row = [
            user.name,
            f'"{user.phone}"',   # forces Excel to show full number
            submitted_at
        ]

        # Add answer for each question in order
        for q in questions:
            row.append(answer_map.get(q.id, ""))

        writer.writerow(row)

    output.seek(0)

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=form_{form_id}_responses.csv"
        }
    )

# ─────────────────────────────────────────
# GET /forms/{form_id}/responses/summary
# Get a clean summary grouped by user
# ─────────────────────────────────────────
@router.get("/{form_id}/responses/summary")
def get_responses_summary(
    form_id: int,
    db:      Session = Depends(get_db)
):
    # Check form exists
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    # Get all questions for this form
    questions = (
        db.query(Question)
        .filter(Question.form_id == form_id)
        .order_by(Question.order)
        .all()
    )

    # Get all users who responded
    user_ids = (
        db.query(Response.user_id)
        .filter(Response.form_id == form_id)
        .distinct()
        .all()
    )

    if not user_ids:
        return {"form_id": form_id, "total_responses": 0, "responses": []}

    summary = []

    for (user_id,) in user_ids:
        user = db.query(User).filter(User.id == user_id).first()

        # Get all answers by this user for this form
        answers = (
            db.query(Response)
            .filter(
                Response.form_id == form_id,
                Response.user_id == user_id
            )
            .all()
        )

        # Map question_id → answer
        answer_map = {a.question_id: a.answer for a in answers}

        user_summary = {
            "user_id":    user.id,
            "user_name":  user.name,
            "user_phone": user.phone,
            "answers": [
                {
                    "question": q.question_text,
                    "answer":   answer_map.get(q.id, "No answer")
                }
                for q in questions
            ]
        }

        summary.append(user_summary)

    return {
        "form_id":         form_id,
        "form_title":      form.title,
        "total_responses": len(summary),
        "responses":       summary
    }