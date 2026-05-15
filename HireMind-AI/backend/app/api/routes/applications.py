from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.resume import Resume, ParsedResumeData, MLPrediction, Application, ApplicationStatus
from app.models.job import Job
from app.models.user import Candidate
from app.schemas.resume import ApplicationCreate, ApplicationOut, ApplicationWithDetails, ApplicationStatusUpdate
from app.core.security import get_current_candidate, get_current_recruiter
from app.services.ml_service import (compute_match_score, find_missing_skills,
                                      generate_ai_feedback, generate_interview_questions)

router = APIRouter(prefix="/api/applications", tags=["Applications"])

# ── Apply for Job ─────────────────────────────────────────────────────
@router.post("", response_model=ApplicationOut)
def apply_for_job(data: ApplicationCreate,
                  candidate=Depends(get_current_candidate),
                  db: Session = Depends(get_db)):
    # Get latest resume
    resume = (db.query(Resume).filter(Resume.candidate_id == candidate.id)
              .order_by(Resume.created_at.desc()).first())
    if not resume:
        raise HTTPException(status_code=400, detail="Please upload a resume first")

    # Check already applied with THIS SPECIFIC resume
    existing = db.query(Application).filter(
        Application.candidate_id == candidate.id,
        Application.job_id == data.job_id,
        Application.resume_id == resume.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied to this job with your current resume.")

    # Get job
    job = db.query(Job).filter(Job.id == data.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get parsed data
    parsed = db.query(ParsedResumeData).filter(ParsedResumeData.resume_id == resume.id).first()
    prediction = db.query(MLPrediction).filter(MLPrediction.resume_id == resume.id).first()

    raw_text = (parsed.raw_text or "") if parsed else ""
    skills = (parsed.skills or []) if parsed else []
    domain = prediction.predicted_domain if prediction else "General"

    # Compute match score
    match_result = compute_match_score(raw_text, job.description, job.required_skills)
    match_score = match_result["match_score"]

    # Missing skills
    missing = find_missing_skills(skills, job.required_skills)

    # AI feedback
    parsed_dict = {
        "projects": parsed.projects if parsed else [],
        "certifications": parsed.certifications if parsed else [],
        "experience": parsed.experience if parsed else [],
    }
    feedback = generate_ai_feedback(skills, parsed_dict, match_score)

    # Interview questions
    interview_qs = generate_interview_questions(domain, skills, job.title)

    # Save application
    application = Application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=resume.id,
        status=ApplicationStatus.pending,
        match_score=match_score,
        missing_skills=missing,
        ai_feedback=feedback,
        interview_questions=interview_qs,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application

# ── My Applications ───────────────────────────────────────────────────
@router.get("/my", response_model=List[ApplicationWithDetails])
def my_applications(candidate=Depends(get_current_candidate), db: Session = Depends(get_db)):
    apps = (db.query(Application)
            .filter(Application.candidate_id == candidate.id)
            .order_by(Application.applied_at.desc()).all())
    result = []
    for app in apps:
        job = db.query(Job).filter(Job.id == app.job_id).first()
        resume = db.query(Resume).filter(Resume.id == app.resume_id).first()
        pred = db.query(MLPrediction).filter(MLPrediction.resume_id == app.resume_id).first()
        result.append(ApplicationWithDetails(
            id=app.id, status=app.status.value, match_score=app.match_score,
            missing_skills=app.missing_skills, ai_feedback=app.ai_feedback,
            interview_questions=app.interview_questions, applied_at=app.applied_at,
            updated_at=app.updated_at,
            candidate_name=candidate.name, candidate_email=candidate.email,
            job_title=job.title if job else None, job_domain=job.domain if job else None,
            resume_filename=resume.filename if resume else None,
            predicted_domain=pred.predicted_domain if pred else None,
        ))
    return result

# ── Get Application Detail ────────────────────────────────────────────
@router.get("/{app_id}")
def get_application(app_id: int, candidate=Depends(get_current_candidate), db: Session = Depends(get_db)):
    app = db.query(Application).filter(
        Application.id == app_id,
        Application.candidate_id == candidate.id
    ).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    job = db.query(Job).filter(Job.id == app.job_id).first()
    return {
        "id": app.id, "status": app.status.value, "match_score": app.match_score,
        "missing_skills": app.missing_skills, "ai_feedback": app.ai_feedback,
        "interview_questions": app.interview_questions,
        "applied_at": str(app.applied_at), "job_title": job.title if job else None,
        "job_domain": job.domain if job else None,
        "job_description": job.description if job else None,
    }

# ── Recruiter: All Applications ───────────────────────────────────────
@router.get("/recruiter/all")
def recruiter_all_applications(recruiter=Depends(get_current_recruiter), db: Session = Depends(get_db)):
    # Get all jobs by this recruiter
    job_ids = [j.id for j in db.query(Job).filter(Job.recruiter_id == recruiter.id).all()]
    apps = db.query(Application).filter(Application.job_id.in_(job_ids)).order_by(Application.applied_at.desc()).all()

    result = []
    for app in apps:
        candidate = db.query(Candidate).filter(Candidate.id == app.candidate_id).first()
        job = db.query(Job).filter(Job.id == app.job_id).first()
        resume = db.query(Resume).filter(Resume.id == app.resume_id).first()
        pred = db.query(MLPrediction).filter(MLPrediction.resume_id == app.resume_id).first()
        result.append({
            "id": app.id,
            "candidate_name": candidate.name if candidate else "Unknown",
            "candidate_email": candidate.email if candidate else "",
            "job_title": job.title if job else "Unknown",
            "job_domain": job.domain if job else "",
            "match_score": app.match_score,
            "predicted_domain": pred.predicted_domain if pred else "",
            "status": app.status.value,
            "resume_id": app.resume_id,
            "resume_filename": resume.filename if resume else "",
            "applied_at": str(app.applied_at),
            "missing_skills": app.missing_skills or [],
        })
    return result

# ── Recruiter: Update Application Status ─────────────────────────────
@router.patch("/{app_id}/status")
def update_application_status(app_id: int, data: ApplicationStatusUpdate,
                               recruiter=Depends(get_current_recruiter),
                               db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Verify job belongs to this recruiter
    job = db.query(Job).filter(Job.id == app.job_id, Job.recruiter_id == recruiter.id).first()
    if not job:
        raise HTTPException(status_code=403, detail="Not authorized")

    app.status = data.status
    db.commit()
    db.refresh(app)
    return {"id": app.id, "status": app.status.value, "message": "Status updated"}
