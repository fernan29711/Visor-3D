from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Configuración global de la aplicación."""

    # Database
    database_url: str = "postgresql://surveyor:surveyor123@localhost:5432/surveyor_db"
    sqlalchemy_echo: bool = False

    # JWT & Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Application
    app_name: str = "Surveyor SaaS"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"

    # API
    api_v1_prefix: str = "/api/v1"

    # Celery
    celery_broker_url: str = "redis://localhost:6379"
    celery_result_backend: str = "redis://localhost:6379"

    # Storage
    storage_backend: str = "local"
    storage_path: str = "./storage"
    max_upload_size_mb: int = 100

    # CORS
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    cors_credentials: bool = True
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]

    # Geospacial
    default_crs: str = "EPSG:4326"
    coordinate_precision: int = 8

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
