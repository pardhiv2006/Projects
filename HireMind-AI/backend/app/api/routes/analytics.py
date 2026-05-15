from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.resume import Application, ApplicationStatus
from app.models.job import Job
from app.models.user import Candidate
from app.core.security import get_current_recruiter

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/recruiter")
def recruiter_analytics(recruiter=Depends(get_current_recruiter), db: Session = Depends(get_db)):
    # Jobs by this recruiter
    job_ids = [j.id for j in db.query(Job).filter(Job.recruiter_id == recruiter.id).all()]
    all_apps = db.query(Application).filter(Application.job_id.in_(job_ids)).all() if job_ids else []

    total = len(all_apps)
    selected = sum(1 for a in all_apps if a.status == ApplicationStatus.selected)
    rejected = sum(1 for a in all_apps if a.status == ApplicationStatus.rejected)
    pending = sum(1 for a in all_apps if a.status == ApplicationStatus.pending)
    active_jobs = db.query(Job).filter(Job.recruiter_id == recruiter.id, Job.is_active == True).count()

    # Average match score
    scores = [a.match_score for a in all_apps if a.match_score is not None]
    avg_match = round(sum(scores) / len(scores), 2) if scores else 0

    # Top applied jobs
    from app.models.resume import Resume, MLPrediction
    job_app_counts = {}
    for app in all_apps:
        job = db.query(Job).filter(Job.id == app.job_id).first()
        if job:
            job_app_counts[job.title] = job_app_counts.get(job.title, 0) + 1
    top_jobs = sorted(job_app_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    # Skills distribution
    from app.models.resume import ParsedResumeData
    skill_counts = {}
    for app in all_apps:
        parsed = db.query(ParsedResumeData).filter(ParsedResumeData.resume_id == app.resume_id).first()
        if parsed and parsed.skills:
            for skill in parsed.skills[:5]:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    # Domain distribution
    domain_counts = {}
    for app in all_apps:
        pred = db.query(MLPrediction).filter(MLPrediction.resume_id == app.resume_id).first()
        if pred and pred.predicted_domain:
            domain_counts[pred.predicted_domain] = domain_counts.get(pred.predicted_domain, 0) + 1

    # Match score distribution
    score_bands = {"0-25": 0, "26-50": 0, "51-75": 0, "76-100": 0}
    for s in scores:
        if s <= 25: score_bands["0-25"] += 1
        elif s <= 50: score_bands["26-50"] += 1
        elif s <= 75: score_bands["51-75"] += 1
        else: score_bands["76-100"] += 1

    return {
        "total_applicants": total,
        "selected": selected,
        "rejected": rejected,
        "pending": pending,
        "active_jobs": active_jobs,
        "avg_match_score": avg_match,
        "top_jobs": [{"name": k, "count": v} for k, v in top_jobs],
        "top_skills": [{"skill": k, "count": v} for k, v in top_skills],
        "domain_distribution": [{"domain": k, "count": v} for k, v in domain_counts.items()],
        "score_distribution": [{"range": k, "count": v} for k, v in score_bands.items()],
    }
