from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.job import Job
from app.models.resume import Application
from app.schemas.job import JobCreate, JobUpdate, JobOut
from app.core.security import get_current_recruiter

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

@router.post("", response_model=JobOut)
def create_job(data: JobCreate, db: Session = Depends(get_db),
               recruiter=Depends(get_current_recruiter)):
    job = Job(**data.model_dump(), recruiter_id=recruiter.id)
    db.add(job)
    db.commit()
    db.refresh(job)
    job.applicant_count = 0
    return job

@router.get("", response_model=List[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).filter(Job.is_active == True).order_by(Job.created_at.desc()).all()
    for job in jobs:
        job.applicant_count = db.query(Application).filter(Application.job_id == job.id).count()
    return jobs

@router.get("/my", response_model=List[JobOut])
def my_jobs(db: Session = Depends(get_db), recruiter=Depends(get_current_recruiter)):
    jobs = db.query(Job).filter(Job.recruiter_id == recruiter.id).order_by(Job.created_at.desc()).all()
    for job in jobs:
        job.applicant_count = db.query(Application).filter(Application.job_id == job.id).count()
    return jobs

@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.applicant_count = db.query(Application).filter(Application.job_id == job_id).count()
    return job

@router.put("/{job_id}", response_model=JobOut)
def update_job(job_id: int, data: JobUpdate, db: Session = Depends(get_db),
               recruiter=Depends(get_current_recruiter)):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == recruiter.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(job, k, v)
    db.commit()
    db.refresh(job)
    job.applicant_count = db.query(Application).filter(Application.job_id == job_id).count()
    return job

@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db),
               recruiter=Depends(get_current_recruiter)):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == recruiter.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"message": "Job deleted"}
