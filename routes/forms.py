from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.form import Form
from schemas.form import FormCreate, FormResponse
from typing import List

router = APIRouter(
    prefix="/forms",
    tags=["Forms"]
)

# ─────────────────────────────────────────
# POST /forms → Create a new form
# ─────────────────────────────────────────
@router.post("/", response_model=FormResponse)
def create_form(form_data: FormCreate, db: Session = Depends(get_db)):
    new_form = Form(
        title=form_data.title,
        description=form_data.description
    )
    db.add(new_form)
    db.commit()
    db.refresh(new_form)
    return new_form


# ─────────────────────────────────────────
# GET /forms → List all forms
# ─────────────────────────────────────────
@router.get("/", response_model=List[FormResponse])
def get_all_forms(db: Session = Depends(get_db)):
    forms = db.query(Form).all()
    return forms


# ─────────────────────────────────────────
# GET /forms/{form_id} → Get one form by ID
# ─────────────────────────────────────────
@router.get("/{form_id}", response_model=FormResponse)
def get_form(form_id: int, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()

    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    return form


# ─────────────────────────────────────────
# DELETE /forms/{form_id} → Delete a form
# ─────────────────────────────────────────
@router.delete("/{form_id}")
def delete_form(form_id: int, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()

    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    db.delete(form)
    db.commit()
    return {"message": f"Form {form_id} deleted successfully"}