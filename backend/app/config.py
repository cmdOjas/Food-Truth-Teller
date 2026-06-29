"""Application configuration for different environments."""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 86400))
    )
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    OPEN_FOOD_FACTS_BASE_URL = os.environ.get(
        "OPEN_FOOD_FACTS_BASE_URL", "https://world.openfoodfacts.org/api/v2"
    )
    ML_MODEL_PATH = os.environ.get("ML_MODEL_PATH", "../ml/models/health_model.pkl")
    ML_VECTORIZER_PATH = os.environ.get(
        "ML_VECTORIZER_PATH", "../ml/models/vectorizer.pkl"
    )
    BCRYPT_LOG_ROUNDS = int(os.environ.get("BCRYPT_LOG_ROUNDS", 12))
    RATELIMIT_DEFAULT = os.environ.get("RATE_LIMIT_PER_MINUTE", "60") + " per minute"
    RATELIMIT_STORAGE_URI = os.environ.get("REDIS_URL", "redis://localhost:6379/0")


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/food_truth_teller",
    )
    SQLALCHEMY_ECHO = False


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=3600)
    RATELIMIT_ENABLED = False
    RATELIMIT_STORAGE_URI = "memory://"


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "")
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://", 1
        )


config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
