from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.form import Form
from services.dashboard_service import (
    get_scan_stats,
    get_completion_stats,
    get_timing_stats,
    get_location_stats,
    get_question_stats
)

router = APIRouter(
    prefix="/forms",
    tags=["Dashboard"]
)


# ─────────────────────────────────────────
# GET /forms/{form_id}/dashboard
# All widget data in one call
# ─────────────────────────────────────────
@router.get("/{form_id}/dashboard")
def get_dashboard(form_id: int, db: Session = Depends(get_db)):

    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    return {
        "form_id":          form.id,
        "form_title":       form.title,
        "form_location":    form.location,
        "form_timer":       form.timer_seconds,
        "is_active":        form.is_active,
        "scan_stats":       get_scan_stats(form_id, db),
        "completion_stats": get_completion_stats(form_id, db),
        "timing_stats":     get_timing_stats(form_id, db),
        "location_stats":   get_location_stats(form_id, db),
        "question_stats":   get_question_stats(form_id, db)
    }


# ─────────────────────────────────────────
# GET /forms/{form_id}/dashboard/scans
# Scan stats only
# ─────────────────────────────────────────
@router.get("/{form_id}/dashboard/scans")
def get_dashboard_scans(form_id: int, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    return get_scan_stats(form_id, db)


# ─────────────────────────────────────────
# GET /forms/{form_id}/dashboard/completions
# Completion stats only
# ─────────────────────────────────────────
@router.get("/{form_id}/dashboard/completions")
def get_dashboard_completions(form_id: int, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    return get_completion_stats(form_id, db)


# ─────────────────────────────────────────
# GET /forms/{form_id}/dashboard/timing
# Timing stats only
# ─────────────────────────────────────────
@router.get("/{form_id}/dashboard/timing")
def get_dashboard_timing(form_id: int, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    return get_timing_stats(form_id, db)


# ─────────────────────────────────────────
# GET /forms/{form_id}/dashboard/locations
# Location stats only
# ─────────────────────────────────────────
@router.get("/{form_id}/dashboard/locations")
def get_dashboard_locations(form_id: int, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    return get_location_stats(form_id, db)


# ─────────────────────────────────────────
# GET /forms/{form_id}/dashboard/questions
# Question answer breakdown only
# ─────────────────────────────────────────
@router.get("/{form_id}/dashboard/questions")
def get_dashboard_questions(form_id: int, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    return get_question_stats(form_id, db)