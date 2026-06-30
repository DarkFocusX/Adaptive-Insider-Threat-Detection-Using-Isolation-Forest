import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Application configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    DATABASE_PATH = os.path.join(BASE_DIR, "database.db")

    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    OPENING_BALANCE = 1000.0
    DEFAULT_TRUST_SCORE = 95.0

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    LOG_FOLDER = os.path.join(BASE_DIR, "logs")
    MODEL_PATH = os.path.join(BASE_DIR, "ml_model", "trained_model.pkl")
