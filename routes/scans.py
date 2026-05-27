from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.scan import Scan
from models.form import Form
from models.user import User
from schemas.scan import ScanCreate, ScanResponse, ScanLinkUser
from typing import List, Optional

router = APIRouter(
    prefix="/scans",
    tags=["Scans"]
)


# ─────────────────────────────────────────
# POST /scans
# Record a QR scan with GPS + fingerprint
# Called immediately when form page loads
# ─────────────────────────────────────────
@router.post("/", response_model=ScanResponse)
def record_scan(
    scan_data: ScanCreate,
    request:   Request,
    db:        Session = Depends(get_db)
):
    # Check form exists
    form = db.query(Form).filter(Form.id == scan_data.form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    # Auto-capture IP address from request
    ip_address = None
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can have multiple IPs — take the first one
        ip_address = forwarded_for.split(",")[0].strip()
    else:
        ip_address = request.client.host if request.client else None

    # Save scan record
    new_scan = Scan(
        form_id=scan_data.form_id,
        user_id=None,                              # not known yet
        latitude=scan_data.latitude,
        longitude=scan_data.longitude,
        device_fingerprint=scan_data.device_fingerprint,
        user_agent=scan_data.user_agent,
        ip_address=ip_address
    )
    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)

    return new_scan


# ─────────────────────────────────────────
# PATCH /scans/{scan_id}/link-user
# Link a scan to a user after OTP verified
# ─────────────────────────────────────────
@router.patch("/{scan_id}/link-user", response_model=ScanResponse)
def link_user_to_scan(
    scan_id:   int,
    link_data: ScanLinkUser,
    db:        Session = Depends(get_db)
):
    # Find scan
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Check user exists
    user = db.query(User).filter(User.id == link_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check user is verified before linking
    if not user.is_verified:
        raise HTTPException(
            status_code=400,
            detail="User is not OTP verified. Cannot link to scan."
        )

    # Link user to scan
    scan.user_id = link_data.user_id
    db.commit()
    db.refresh(scan)

    return scan


# ─────────────────────────────────────────
# GET /scans/form/{form_id}
# Get all scans for a form (admin)
# ─────────────────────────────────────────
@router.get("/form/{form_id}", response_model=List[ScanResponse])
def get_scans_for_form(
    form_id: int,
    db:      Session = Depends(get_db)
):
    # Check form exists
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    scans = (
        db.query(Scan)
        .filter(Scan.form_id == form_id)
        .order_by(Scan.scanned_at.desc())
        .all()
    )

    return scans


# ─────────────────────────────────────────
# GET /scans/form/{form_id}/stats
# Quick scan stats for a form
# ─────────────────────────────────────────
@router.get("/form/{form_id}/stats")
def get_scan_stats(
    form_id: int,
    db:      Session = Depends(get_db)
):
    # Check form exists
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    total_scans = (
        db.query(Scan)
        .filter(Scan.form_id == form_id)
        .count()
    )

    unique_users = (
        db.query(Scan.user_id)
        .filter(
            Scan.form_id == form_id,
            Scan.user_id != None
        )
        .distinct()
        .count()
    )

    scans_with_gps = (
        db.query(Scan)
        .filter(
            Scan.form_id == form_id,
            Scan.latitude != None,
            Scan.longitude != None
        )
        .count()
    )

    scans_without_gps = total_scans - scans_with_gps

    return {
        "form_id":             form_id,
        "total_scans":         total_scans,
        "unique_users_linked": unique_users,
        "scans_with_gps":      scans_with_gps,
        "scans_without_gps":   scans_without_gps
    }