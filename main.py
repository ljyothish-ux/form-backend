from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

# Import all models
from models.form import Form
from models.question import Question
from models.user import User
from models.response import Response
from models.otp_verification import OTPVerification
from models.scan import Scan
from models.form_session import FormSession

# Import all routers
from routes.forms import router as forms_router
from routes.questions import router as questions_router
from routes.users import router as users_router
from routes.responses import router as responses_router
from routes.qr import router as qr_router
from routes.otp import router as otp_router
from routes.scans import router as scans_router
from routes.sessions import router as sessions_router
from routes.dashboard import router as dashboard_router    # ← new


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables ready")
    yield


app = FastAPI(
    title="Form Backend API",
    description="Dynamic form system with QR code support",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API is running", "version": "2.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "2.0.0"}

# Register all routers
app.include_router(forms_router)
app.include_router(questions_router)
app.include_router(users_router)
app.include_router(responses_router)
app.include_router(qr_router)
app.include_router(otp_router)
app.include_router(scans_router)
app.include_router(sessions_router)
app.include_router(dashboard_router)                       # ← new