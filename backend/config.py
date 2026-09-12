import os
from dotenv import load_dotenv

# Load .env file from backend root if present
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Try importing Config from app.config to preserve compatibility
try:
    from app.config import Config as AppConfig
    BaseConfig = AppConfig
except ImportError:
    class BaseConfig:
        SQLALCHEMY_DATABASE_URI = os.getenv(
            "DATABASE_URL",
            "postgresql://localhost:5432/bizmate"
        )
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SECRET_KEY = os.getenv("SECRET_KEY", "")
        JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")


class Config(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        getattr(BaseConfig, "SQLALCHEMY_DATABASE_URI", "postgresql://localhost:5432/bizmate")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", getattr(BaseConfig, "SECRET_KEY", ""))
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", getattr(BaseConfig, "JWT_SECRET_KEY", ""))
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

