from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="BatchFlow")
    environment: str = Field(default="local")  # local/staging/prod

    database_url: str = Field(
        ...,
        validation_alias="DATABASE_URL",
        description="mysql+pymysql://user:pass@host/db",
    )

    # API hardening
    rate_limit_enabled: bool = Field(default=False, validation_alias="RATE_LIMIT_ENABLED")
    rate_limit_rpm: int = Field(default=120, validation_alias="RATE_LIMIT_RPM")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
