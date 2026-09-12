import os
from dotenv import load_dotenv

# ==========================================================
# Load .env
# ==========================================================

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


# ==========================================================
# Base Config
# ==========================================================

try:
    from app.config import Config as AppConfig
    BaseConfig = AppConfig
except ImportError:

    class BaseConfig:
        SQLALCHEMY_DATABASE_URI = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:kushagrapostgre@localhost:5432/bizmate"
        )

        SQLALCHEMY_TRACK_MODIFICATIONS = False

        SECRET_KEY = os.getenv(
            "SECRET_KEY",
            "super-secret-bizmate-key-2026"
        )

        JWT_SECRET_KEY = os.getenv(
            "JWT_SECRET_KEY",
            "super-secret-jwt-key-2026"
        )


# ==========================================================
# Application Config
# ==========================================================

class Config(BaseConfig):

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        getattr(
            BaseConfig,
            "SQLALCHEMY_DATABASE_URI",
            "postgresql://postgres:kushagrapostgre@localhost:5432/bizmate",
        ),
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        getattr(
            BaseConfig,
            "SECRET_KEY",
            "super-secret-bizmate-key-2026",
        ),
    )

    # JWT
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        getattr(
            BaseConfig,
            "JWT_SECRET_KEY",
            "super-secret-jwt-key-2026",
        ),
    )

    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # Upload size (16 MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Frontend URLs (comma-separated in .env)
    FRONTEND_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "FRONTEND_ORIGINS",
            "http://localhost:8081,http://127.0.0.1:8081"
        ).split(",")
        if origin.strip()
    ]

    # Debug
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # Environment
    ENV = os.getenv("FLASK_ENV", "development")