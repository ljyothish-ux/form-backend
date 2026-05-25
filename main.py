from fastapi import FastAPI
from database import engine, Base

# Import models
from models.form import Form
from models.question import Question
from models.user import User
from models.response import Response

# Import routers
from routes.forms import router as forms_router
from routes.questions import router as questions_router

app = FastAPI(
    title="Form Backend API",
    description="Dynamic form system with QR code support",
    version="1.0.0"
)

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables ready")

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

# Register routers
app.include_router(forms_router)
app.include_router(questions_router)