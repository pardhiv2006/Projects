from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.database import get_db
from app.models.user import Recruiter, Candidate
from app.schemas.auth import (RecruiterCreate, RecruiterLogin, CandidateCreate,
                               CandidateLogin, Token, RecruiterOut, CandidateOut)
from app.core.security import (get_password_hash, verify_password, create_access_token,
                                get_current_recruiter, get_current_candidate)
from app.core.config import settings

router = APIRouter(prefix="/api/auth", tags=["Auth"])

# ── Recruiter Registration ─────────────────────────────────────────────
@router.post("/recruiter/register", response_model=Token)
def recruiter_register(data: RecruiterCreate, db: Session = Depends(get_db)):
    if db.query(Recruiter).filter(Recruiter.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    recruiter = Recruiter(
        name=data.name,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        company=data.company,
    )
    db.add(recruiter)
    db.commit()
    db.refresh(recruiter)
    token = create_access_token({"sub": str(recruiter.id), "role": "recruiter"})
    return {"access_token": token, "token_type": "bearer", "role": "recruiter",
            "user": {"id": recruiter.id, "name": recruiter.name, "email": recruiter.email,
                     "company": recruiter.company}}

# ── Recruiter Login ────────────────────────────────────────────────────
@router.post("/recruiter/login", response_model=Token)
def recruiter_login(data: RecruiterLogin, db: Session = Depends(get_db)):
    # Check for hardcoded admin credentials
    if data.email == "admin" and data.password == "admin123":
        recruiter = db.query(Recruiter).filter(Recruiter.email == "admin").first()
        if not recruiter:
            # Create a default admin recruiter if it doesn't exist
            recruiter = Recruiter(
                name="Admin Recruiter",
                email="admin",
                hashed_password=get_password_hash("admin123"),
                company="HireMind Admin"
            )
            db.add(recruiter)
            db.commit()
            db.refresh(recruiter)
    else:
        recruiter = db.query(Recruiter).filter(Recruiter.email == data.email).first()
        if not recruiter or not verify_password(data.password, recruiter.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
    token = create_access_token({"sub": str(recruiter.id), "role": "recruiter"})
    return {"access_token": token, "token_type": "bearer", "role": "recruiter",
            "user": {"id": recruiter.id, "name": recruiter.name, "email": recruiter.email,
                     "company": recruiter.company}}

# ── Candidate Registration ─────────────────────────────────────────────
@router.post("/candidate/register", response_model=Token)
def candidate_register(data: CandidateCreate, db: Session = Depends(get_db)):
    if db.query(Candidate).filter(Candidate.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    candidate = Candidate(
        name=data.name,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        phone=data.phone,
        location=data.location,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    token = create_access_token({"sub": str(candidate.id), "role": "candidate"})
    return {"access_token": token, "token_type": "bearer", "role": "candidate",
            "user": {"id": candidate.id, "name": candidate.name, "email": candidate.email,
                     "phone": candidate.phone, "location": candidate.location, "bio": candidate.bio}}

# ── Candidate Login ────────────────────────────────────────────────────
@router.post("/candidate/login", response_model=Token)
def candidate_login(data: CandidateLogin, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.email == data.email).first()
    if not candidate or not verify_password(data.password, candidate.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(candidate.id), "role": "candidate"})
    return {"access_token": token, "token_type": "bearer", "role": "candidate",
            "user": {"id": candidate.id, "name": candidate.name, "email": candidate.email,
                     "phone": candidate.phone, "location": candidate.location, "bio": candidate.bio}}

# ── Me Endpoints ───────────────────────────────────────────────────────
@router.get("/recruiter/me", response_model=RecruiterOut)
def recruiter_me(current=Depends(get_current_recruiter)):
    return current

@router.get("/candidate/me", response_model=CandidateOut)
def candidate_me(current=Depends(get_current_candidate)):
    return current
