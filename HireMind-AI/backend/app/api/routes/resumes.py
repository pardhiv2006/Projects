import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.resume import Resume, ParsedResumeData, MLPrediction, Application, ApplicationStatus
from app.models.job import Job
from app.schemas.resume import ResumeOut, ParsedResumeOut, MLPredictionOut, ApplicationOut, ApplicationWithDetails, ApplicationCreate, ApplicationStatusUpdate
from app.core.security import get_current_candidate, get_current_recruiter
from app.core.config import settings
from app.services.resume_parser import parse_resume
from app.services.ml_service import (predict_domain, compute_match_score,
                                      find_missing_skills, generate_ai_feedback,
                                      generate_interview_questions)

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])

# ── Upload Resume ─────────────────────────────────────────────────────
@router.post("/upload", response_model=ResumeOut)
async def upload_resume(file: UploadFile = File(...),
                         candidate=Depends(get_current_candidate),
                         db: Session = Depends(get_db)):
    allowed = ["pdf", "docx", "doc"]
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="Only PDF/DOCX files allowed")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_bytes = await file.read()
    safe_name = f"{candidate.id}_{file.filename.replace(' ', '_')}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_name)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # Save resume record
    resume = Resume(
        candidate_id=candidate.id,
        filename=file.filename,
        file_path=file_path,
        file_size=len(file_bytes),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    # Parse resume
    parsed = parse_resume(file_bytes, file.filename)
    parsed_record = ParsedResumeData(
        resume_id=resume.id,
        raw_text=parsed["raw_text"],
        skills=parsed["skills"],
        education=parsed["education"],
        experience=parsed["experience"],
        projects=parsed["projects"],
        certifications=parsed["certifications"],
    )
    db.add(parsed_record)
    db.commit()

    # ML domain prediction
    prediction = predict_domain(parsed["raw_text"], parsed["skills"])
    ml_record = MLPrediction(
        resume_id=resume.id,
        predicted_domain=prediction["predicted_domain"],
        confidence_score=prediction["confidence_score"],
        all_predictions=prediction["all_predictions"],
    )
    db.add(ml_record)
    db.commit()

    return resume

# ── Get My Resumes ────────────────────────────────────────────────────
@router.get("/my", response_model=List[ResumeOut])
def my_resumes(candidate=Depends(get_current_candidate), db: Session = Depends(get_db)):
    return db.query(Resume).filter(Resume.candidate_id == candidate.id).order_by(Resume.created_at.desc()).all()

# ── Get Latest Resume With Full Data ─────────────────────────────────
@router.get("/my/latest")
def latest_resume(candidate=Depends(get_current_candidate), db: Session = Depends(get_db)):
    resume = (db.query(Resume).filter(Resume.candidate_id == candidate.id)
              .order_by(Resume.created_at.desc()).first())
    if not resume:
        return {"resume": None}
    parsed = db.query(ParsedResumeData).filter(ParsedResumeData.resume_id == resume.id).first()
    prediction = db.query(MLPrediction).filter(MLPrediction.resume_id == resume.id).first()
    return {
        "resume": {"id": resume.id, "filename": resume.filename, "created_at": str(resume.created_at)},
        "parsed": {
            "skills": parsed.skills if parsed else [],
            "education": parsed.education if parsed else [],
            "experience": parsed.experience if parsed else [],
            "projects": parsed.projects if parsed else [],
            "certifications": parsed.certifications if parsed else [],
        },
        "prediction": {
            "predicted_domain": prediction.predicted_domain if prediction else None,
            "confidence_score": prediction.confidence_score if prediction else None,
            "all_predictions": prediction.all_predictions if prediction else {},
        }
    }

# ── Download Resume ───────────────────────────────────────────────────
@router.get("/download/{resume_id}")
def download_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume or not os.path.exists(resume.file_path):
        raise HTTPException(status_code=404, detail="Resume not found")
    return FileResponse(resume.file_path, filename=resume.filename,
                        media_type="application/octet-stream")

# ── Recommend Jobs ────────────────────────────────────────────────────
@router.get("/recommendations")
def recommend_jobs(candidate=Depends(get_current_candidate), db: Session = Depends(get_db)):
    resume = (db.query(Resume).filter(Resume.candidate_id == candidate.id)
              .order_by(Resume.created_at.desc()).first())
    
    prediction = db.query(MLPrediction).filter(MLPrediction.resume_id == resume.id).first() if resume else None
    parsed = db.query(ParsedResumeData).filter(ParsedResumeData.resume_id == resume.id).first() if resume else None
    
    domain = prediction.predicted_domain if prediction else None
    all_jobs = db.query(Job).filter(Job.is_active == True).all()

    scored_jobs = []
    skills_text = " ".join(parsed.skills or []) if parsed else ""
    raw_text = (parsed.raw_text or "") if parsed else ""

    for job in all_jobs:
        if resume:
            is_domain_match = (domain and job.domain and domain.lower() in job.domain.lower()) or \
                              (domain and job.domain and job.domain.lower() in domain.lower())
            match = compute_match_score(raw_text or skills_text, job.description, job.required_skills)
            score = match["match_score"]
        else:
            is_domain_match = False
            score = 0

        scored_jobs.append({
            "id": job.id, "title": job.title, "domain": job.domain,
            "required_skills": job.required_skills, "location": job.location,
            "experience_years": job.experience_years, "salary_min": job.salary_min,
            "salary_max": job.salary_max, "match_score": score,
            "is_recommended": is_domain_match,
            "created_at": str(job.created_at),
        })

    scored_jobs.sort(key=lambda x: (x["is_recommended"], x["match_score"]), reverse=True)
    return {"jobs": scored_jobs[:20], "predicted_domain": domain}
