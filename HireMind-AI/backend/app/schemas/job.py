from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class JobCreate(BaseModel):
    title: str
    description: str
    required_skills: str
    experience_years: int = 0
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    domain: Optional[str] = None
    deadline: Optional[datetime] = None

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[str] = None
    experience_years: Optional[int] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    domain: Optional[str] = None
    is_active: Optional[bool] = None
    deadline: Optional[datetime] = None

class JobOut(BaseModel):
    id: int
    recruiter_id: int
    title: str
    description: str
    required_skills: str
    experience_years: int
    location: Optional[str]
    salary_min: Optional[int]
    salary_max: Optional[int]
    domain: Optional[str]
    is_active: bool
    deadline: Optional[datetime]
    created_at: datetime
    applicant_count: Optional[int] = 0

    class Config:
        from_attributes = True
