from fastapi import FastAPI

app = FastAPI(
    title="Form Backend API",
    description="Dynamic form system with QR code support",
    version="1.0.0"
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