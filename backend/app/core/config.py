import os
import socket
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    APP_NAME: str = "Tinvix Catalog API"
    INSTANCE_ID: str = Field(default_factory=lambda: f"{socket.gethostname()}-{os.getpid()}")

    # Security: Secret required to create products via API
    ADMIN_API_KEY: str = Field(default="tinvix_secret_admin_key_2026")

    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "tinvix_db"

    # MinIO S3
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "products"
    MINIO_SECURE: bool = False
    # If set to relative path (default), images work seamlessly on localhost, mobile TMA, and tunnels!
    MINIO_PUBLIC_URL: str = "/storage/products"
    PUBLIC_BASE_URL: str = ""

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
