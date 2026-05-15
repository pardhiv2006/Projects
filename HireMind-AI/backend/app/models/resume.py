from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class ApplicationStatus(str, enum.Enum):
    pending = "pending"
    selected = "selected"
    rejected = "rejected"

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    candidate = relationship("Candidate", back_populates="resumes")
    parsed_data = relationship("ParsedResumeData", back_populates="resume", uselist=False, cascade="all, delete-orphan")
    ml_prediction = relationship("MLPrediction", back_populates="resume", uselist=False, cascade="all, delete-orphan")


class ParsedResumeData(Base):
    __tablename__ = "parsed_resume_data"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    raw_text = Column(Text, nullable=True)
    skills = Column(JSON, nullable=True)          # list of skills
    education = Column(JSON, nullable=True)       # list of education entries
    experience = Column(JSON, nullable=True)      # list of experience entries
    projects = Column(JSON, nullable=True)        # list of projects
    certifications = Column(JSON, nullable=True)  # list of certifications
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume", back_populates="parsed_data")


class MLPrediction(Base):
    __tablename__ = "ml_predictions"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    predicted_domain = Column(String(100), nullable=True)
    confidence_score = Column(Float, nullable=True)
    all_predictions = Column(JSON, nullable=True)   # {domain: probability}
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume", back_populates="ml_prediction")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.pending, nullable=False)
    match_score = Column(Float, nullable=True)
    missing_skills = Column(JSON, nullable=True)
    ai_feedback = Column(JSON, nullable=True)
    interview_questions = Column(JSON, nullable=True)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    candidate = relationship("Candidate", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume")
