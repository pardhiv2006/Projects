from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./hiremind.db"
    SECRET_KEY: str = "hiremind-super-secret-jwt-key-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    UPLOAD_DIR: str = "uploads"
    MODELS_DIR: str = "models"
    ML_MODEL_PATH: str = "models/model.pkl"
    VECTORIZER_PATH: str = "models/vectorizer.pkl"
    LABEL_ENCODER_PATH: str = "models/label_encoder.pkl"

    class Config:
        env_file = ".env"

settings = Settings()
