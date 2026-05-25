from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from models.form import Form
from services.qr_service import generate_qr
import io
import os

router = APIRouter(
    prefix="/forms",
    tags=["QR Code"]
)

# Base URL where your frontend is hosted
# During development this points to localhost
# On Render this will be your live frontend URL
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")


# ─────────────────────────────────────────
# GET /forms/{form_id}/qr
# Returns QR code as PNG image
# ─────────────────────────────────────────
@router.get("/{form_id}/qr")
def get_qr_code(
    form_id: int,
    db: Session = Depends(get_db)
):
    # Check form exists
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    # Build the URL that QR will encode
    form_url = f"{FRONTEND_BASE_URL}/form/{form_id}"

    # Generate QR bytes
    qr_bytes = generate_qr(form_url)

    # Return as PNG image directly in browser
    return Response(
        content=qr_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": f"inline; filename=form_{form_id}_qr.png"
        }
    )


# ─────────────────────────────────────────
# GET /forms/{form_id}/qr/download
# Downloads QR code as PNG file
# ─────────────────────────────────────────
@router.get("/{form_id}/qr/download")
def download_qr_code(
    form_id: int,
    db: Session = Depends(get_db)
):
    # Check form exists
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    # Build the URL that QR will encode
    form_url = f"{FRONTEND_BASE_URL}/form/{form_id}"

    # Generate QR bytes
    qr_bytes = generate_qr(form_url)

    # Return as downloadable file
    return StreamingResponse(
        io.BytesIO(qr_bytes),
        media_type="image/png",
        headers={
            "Content-Disposition": f"attachment; filename=form_{form_id}_qr.png"
        }
    )


# ─────────────────────────────────────────
# GET /forms/{form_id}/qr/info
# Returns QR info as JSON (URL encoded + form details)
# ─────────────────────────────────────────
@router.get("/{form_id}/qr/info")
def get_qr_info(
    form_id: int,
    db: Session = Depends(get_db)
):
    # Check form exists
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    form_url = f"{FRONTEND_BASE_URL}/form/{form_id}"

    return {
        "form_id":    form_id,
        "form_title": form.title,
        "qr_url":     form_url,
        "qr_image":   f"/forms/{form_id}/qr",
        "qr_download": f"/forms/{form_id}/qr/download"
    }