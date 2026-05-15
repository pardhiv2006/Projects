from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import get_db

import bcrypt
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/candidate/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from app.models.user import Recruiter, Candidate
    payload = decode_token(token)
    user_id: int = payload.get("sub")
    role: str = payload.get("role")
    if not user_id or not role:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    if role == "recruiter":
        user = db.query(Recruiter).filter(Recruiter.id == int(user_id)).first()
    else:
        user = db.query(Candidate).filter(Candidate.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def get_current_recruiter(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from app.models.user import Recruiter
    payload = decode_token(token)
    user_id = payload.get("sub")
    role = payload.get("role")
    if role != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiter access only")
    user = db.query(Recruiter).filter(Recruiter.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Recruiter not found")
    return user

async def get_current_candidate(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from app.models.user import Candidate
    payload = decode_token(token)
    user_id = payload.get("sub")
    role = payload.get("role")
    if role != "candidate":
        raise HTTPException(status_code=403, detail="Candidate access only")
    user = db.query(Candidate).filter(Candidate.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Candidate not found")
    return user
