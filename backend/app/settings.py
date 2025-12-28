from __future__ import annotations

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = Field(default="BatchFlow")
    environment: str = Field(default="local")  # local/staging/prod
    database_url: str = Field(..., env="DATABASE_URL")  # mysql+pymysql://user:pass@host/db

    # API hardening
    rate_limit_enabled: bool = Field(default=False, env="RATE_LIMIT_ENABLED")
    rate_limit_rpm: int = Field(default=120, env="RATE_LIMIT_RPM")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
