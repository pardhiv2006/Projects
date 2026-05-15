from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ── Recruiter Schemas ──────────────────────────────────────────────────
class RecruiterCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    company: Optional[str] = None

class RecruiterLogin(BaseModel):
    email: str
    password: str

class RecruiterOut(BaseModel):
    id: int
    name: str
    email: str
    company: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# ── Candidate Schemas ──────────────────────────────────────────────────
class CandidateCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    location: Optional[str] = None

class CandidateLogin(BaseModel):
    email: EmailStr
    password: str

class CandidateOut(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    location: Optional[str]
    bio: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None

# ── Token Schemas ──────────────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user: dict
