from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.form import Form
from schemas.form import FormCreate, FormResponse, FormUpdate
from typing import List

router = APIRouter(
    prefix="/forms",
    tags=["Forms"]
)


@router.post("/", response_model=FormResponse, status_code=201)
def create_form(form_data: FormCreate, db: Session = Depends(get_db)):
    new_form = Form(
        title=form_data.title,
        description=form_data.description,
        location=form_data.location,
        timer_seconds=form_data.timer_seconds,
        is_active=form_data.is_active if form_data.is_active is not None else True
    )
    db.add(new_form)
    db.commit()
    db.refresh(new_form)
    return new_form


@router.get("/", response_model=List[FormResponse])
def get_all_forms(db: Session = Depends(get_db)):
    return db.query(Form).all()


@router.get("/{form_id}", response_model=FormResponse)
def get_form(form_id: int, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    return form


# ─────────────────────────────────────────
# PUT /forms/{form_id}
# Update form details including timer
# ─────────────────────────────────────────
@router.put("/{form_id}", response_model=FormResponse)
def update_form(
    form_id:   int,
    form_data: FormUpdate,
    db:        Session = Depends(get_db)
):
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    # Only update fields that were actually sent
    if form_data.title is not None:
        form.title = form_data.title
    if form_data.description is not None:
        form.description = form_data.description
    if form_data.location is not None:
        form.location = form_data.location
    if form_data.timer_seconds is not None:
        form.timer_seconds = form_data.timer_seconds
    if form_data.is_active is not None:
        form.is_active = form_data.is_active

    db.commit()
    db.refresh(form)
    return form


# ─────────────────────────────────────────
# PATCH /forms/{form_id}/toggle
# Flip is_active true ↔ false
# ─────────────────────────────────────────
@router.patch("/{form_id}/toggle")
def toggle_form(form_id: int, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    form.is_active = not form.is_active
    db.commit()
    db.refresh(form)

    return {
        "form_id":   form_id,
        "is_active": form.is_active,
        "message":   f"Form {'activated' if form.is_active else 'deactivated'} successfully"
    }


@router.delete("/{form_id}")
def delete_form(form_id: int, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    db.delete(form)
    db.commit()
    return {"message": f"Form {form_id} deleted successfully"}