from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from database import get_db
from models.form_session import FormSession
from models.form import Form
from models.user import User
from models.scan import Scan
from schemas.session import SessionCreate, SessionResponse, SessionComplete
from datetime import datetime
router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)


# ─────────────────────────────────────────
# POST /sessions
# Create session when user starts the form
# ─────────────────────────────────────────
@router.post("/", response_model=SessionResponse)
def create_session(
    data: SessionCreate,
    db:   DBSession = Depends(get_db)
):
    # Check form exists and is active
    form = db.query(Form).filter(Form.id == data.form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    if not form.is_active:
        raise HTTPException(status_code=400, detail="This form is no longer active")

    # Check user exists and is verified
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_verified:
        raise HTTPException(status_code=400, detail="User is not OTP verified")

    # Check scan exists if provided
    if data.scan_id:
        scan = db.query(Scan).filter(Scan.id == data.scan_id).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")

    # Create session
    new_session = FormSession(
        form_id=data.form_id,
        user_id=data.user_id,
        scan_id=data.scan_id
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # Build response — include timer_seconds from form
    # so frontend knows how long the countdown should be
    response_data = SessionResponse(
        id=new_session.id,
        form_id=new_session.form_id,
        user_id=new_session.user_id,
        scan_id=new_session.scan_id,
        started_at=new_session.started_at,
        submitted_at=new_session.submitted_at,
        time_taken_seconds=new_session.time_taken_seconds,
        is_completed=new_session.is_completed,
        is_timed_out=new_session.is_timed_out,
        timer_seconds=form.timer_seconds   # ← key field for frontend
    )

    return response_data


# ─────────────────────────────────────────
# PATCH /sessions/{session_id}/complete
# Called when user manually submits form
# ─────────────────────────────────────────
@router.patch("/{session_id}/complete", response_model=SessionResponse)
def complete_session(
    session_id: int,
    data:       SessionComplete,
    db:         DBSession = Depends(get_db)
):
    session = db.query(FormSession).filter(FormSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.is_completed:
        raise HTTPException(status_code=400, detail="Session already completed")

    # Strip timezone from everything — make all naive datetimes
    now_naive = datetime.utcnow()

    if data.submitted_at:
        submitted_at = data.submitted_at
        if hasattr(submitted_at, 'tzinfo') and submitted_at.tzinfo is not None:
            submitted_at = submitted_at.replace(tzinfo=None)
    else:
        submitted_at = now_naive

    # Strip timezone from started_at too
    started = session.started_at
    if hasattr(started, 'tzinfo') and started.tzinfo is not None:
        started = started.replace(tzinfo=None)

    time_taken = int((submitted_at - started).total_seconds())

    session.is_completed       = True
    session.is_timed_out       = False
    session.submitted_at       = submitted_at
    session.time_taken_seconds = time_taken

    db.commit()
    db.refresh(session)

    # Get timer_seconds from form for response
    form = db.query(Form).filter(Form.id == session.form_id).first()

    return SessionResponse(
        id=session.id,
        form_id=session.form_id,
        user_id=session.user_id,
        scan_id=session.scan_id,
        started_at=session.started_at,
        submitted_at=session.submitted_at,
        time_taken_seconds=session.time_taken_seconds,
        is_completed=session.is_completed,
        is_timed_out=session.is_timed_out,
        timer_seconds=form.timer_seconds if form else None
    )


# ─────────────────────────────────────────
# PATCH /sessions/{session_id}/timeout
# Called when timer hits zero
# Auto submits whatever was answered
# ─────────────────────────────────────────
@router.patch("/{session_id}/timeout", response_model=SessionResponse)
def timeout_session(
    session_id: int,
    db:         DBSession = Depends(get_db)
):
    session = db.query(FormSession).filter(FormSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.is_completed:
        raise HTTPException(status_code=400, detail="Session already completed")

    submitted_at = datetime.utcnow()  # always naive

    started = session.started_at
    if hasattr(started, 'tzinfo') and started.tzinfo is not None:
        started = started.replace(tzinfo=None)

    time_taken = int((submitted_at - started).total_seconds())

    session.is_completed       = True
    session.is_timed_out       = True     # ← marks as timed out
    session.submitted_at       = submitted_at
    session.time_taken_seconds = time_taken

    db.commit()
    db.refresh(session)

    form = db.query(Form).filter(Form.id == session.form_id).first()

    return SessionResponse(
        id=session.id,
        form_id=session.form_id,
        user_id=session.user_id,
        scan_id=session.scan_id,
        started_at=session.started_at,
        submitted_at=session.submitted_at,
        time_taken_seconds=session.time_taken_seconds,
        is_completed=session.is_completed,
        is_timed_out=session.is_timed_out,
        timer_seconds=form.timer_seconds if form else None
    )


# ─────────────────────────────────────────
# GET /sessions/form/{form_id}
# Get all sessions for a form (admin)
# ─────────────────────────────────────────
@router.get("/form/{form_id}")
def get_sessions_for_form(
    form_id: int,
    db:      DBSession = Depends(get_db)
):
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    sessions = (
        db.query(FormSession)
        .filter(FormSession.form_id == form_id)
        .order_by(FormSession.started_at.desc())
        .all()
    )

    return {
        "form_id":       form_id,
        "total_sessions": len(sessions),
        "sessions": [
            {
                "id":                 s.id,
                "user_id":            s.user_id,
                "scan_id":            s.scan_id,
                "started_at":         s.started_at,
                "submitted_at":       s.submitted_at,
                "time_taken_seconds": s.time_taken_seconds,
                "is_completed":       s.is_completed,
                "is_timed_out":       s.is_timed_out
            }
            for s in sessions
        ]
    }