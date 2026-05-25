from fastapi import FastAPI
from database import engine, Base

# Import all models so SQLAlchemy knows about them
from models.form import Form
from models.question import Question
from models.user import User
from models.response import Response

app = FastAPI(
    title="Form Backend API",
    description="Dynamic form system with QR code support",
    version="1.0.0"
)

# This creates all tables in form_app.db on startup
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }