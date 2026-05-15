from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from app.models.resume import ApplicationStatus

class ResumeOut(BaseModel):
    id: int
    candidate_id: int
    filename: str
    created_at: datetime

    class Config:
        from_attributes = True

class ParsedResumeOut(BaseModel):
    id: int
    resume_id: int
    skills: Optional[List[str]]
    education: Optional[List[Any]]
    experience: Optional[List[Any]]
    projects: Optional[List[Any]]
    certifications: Optional[List[Any]]

    class Config:
        from_attributes = True

class MLPredictionOut(BaseModel):
    id: int
    resume_id: int
    predicted_domain: Optional[str]
    confidence_score: Optional[float]
    all_predictions: Optional[dict]

    class Config:
        from_attributes = True

class ApplicationCreate(BaseModel):
    job_id: int

class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus

class ApplicationOut(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    resume_id: int
    status: str
    match_score: Optional[float]
    missing_skills: Optional[List[str]]
    ai_feedback: Optional[Any]
    interview_questions: Optional[Any]
    applied_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class ApplicationWithDetails(BaseModel):
    id: int
    status: str
    match_score: Optional[float]
    missing_skills: Optional[List[str]]
    ai_feedback: Optional[Any]
    interview_questions: Optional[Any]
    applied_at: datetime
    updated_at: Optional[datetime]
    candidate_name: Optional[str]
    candidate_email: Optional[str]
    job_title: Optional[str]
    job_domain: Optional[str]
    resume_filename: Optional[str]
    predicted_domain: Optional[str]

    class Config:
        from_attributes = True
