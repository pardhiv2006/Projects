from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.db.database import engine, Base
from app.models import *  # ensure all models are registered
from app.api.routes import auth, jobs, resumes, applications, analytics, candidates
from app.core.config import settings

# Create DB tables
Base.metadata.create_all(bind=engine)

# Create dirs
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)

app = FastAPI(
    title="HireMind AI API",
    description="AI-Powered Recruitment & Career Recommendation Platform",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3002",
        "http://localhost:3005",
        "http://localhost:3006",
        "http://localhost:3007",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for resume downloads
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(resumes.router)
app.include_router(applications.router)
app.include_router(analytics.router)
app.include_router(candidates.router)

@app.get("/")
def root():
    return {"message": "HireMind AI API is running", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}
