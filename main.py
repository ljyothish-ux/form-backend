from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

# Import models
from models.form import Form
from models.question import Question
from models.user import User
from models.response import Response

# Import routers
from routes.forms import router as forms_router
from routes.questions import router as questions_router
from routes.users import router as users_router
from routes.responses import router as responses_router
from routes.qr import router as qr_router


# Modern startup event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables ready")
    yield
    # On shutdown (nothing needed for now)


app = FastAPI(
    title="Form Backend API",
    description="Dynamic form system with QR code support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS — allows frontend to talk to this API
# During dev allows everything
# Tighten this in production later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
app.include_router(users_router)
app.include_router(responses_router)
app.include_router(qr_router)