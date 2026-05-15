from app.db.database import Base
from app.models.user import Recruiter, Candidate
from app.models.job import Job
from app.models.resume import Resume, ParsedResumeData, MLPrediction, Application

__all__ = ["Base", "Recruiter", "Candidate", "Job", "Resume", "ParsedResumeData", "MLPrediction", "Application"]
