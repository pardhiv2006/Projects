from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import Candidate
from app.schemas.auth import CandidateUpdate, CandidateOut
from app.core.security import get_current_candidate

router = APIRouter(prefix="/api/candidates", tags=["Candidates"])

@router.get("/me", response_model=CandidateOut)
def get_profile(candidate=Depends(get_current_candidate)):
    return candidate

@router.put("/me", response_model=CandidateOut)
def update_profile(data: CandidateUpdate,
                   candidate=Depends(get_current_candidate),
                   db: Session = Depends(get_db)):
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(candidate, k, v)
    db.commit()
    db.refresh(candidate)
    return candidate
