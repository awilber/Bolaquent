import os
from pathlib import Path


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"

    # Database
    BASE_DIR = Path(__file__).parent
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or f"sqlite:///{BASE_DIR}/bolaquent.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload folders
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Age tier settings
    DEFAULT_TIER = 3  # Elementary as default
    MAX_TIER = 6
    MIN_TIER = 1

    # Learning system
    WORDS_PER_SESSION = {
        1: 5,  # Early Verbal
        2: 8,  # Preschool
        3: 12,  # Elementary
        4: 15,  # Middle School
        5: 20,  # High School
        6: 25,  # Adult
    }

    SESSION_TIMEOUT_MINUTES = {
        1: 5,  # Early Verbal
        2: 10,  # Preschool
        3: 15,  # Elementary
        4: 25,  # Middle School
        5: 30,  # High School
        6: 45,  # Adult
    }
