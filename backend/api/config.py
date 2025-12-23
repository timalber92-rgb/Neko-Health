"""
Configuration Management for HealthGuard API

This module centralizes all configuration using pydantic-settings for
environment-based configuration with validation and type safety.
"""

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via environment variables or .env file.
    Defaults are provided for development environments.
    """

    # API Configuration
    api_title: str = Field(default="HealthGuard API", description="API title")
    api_description: str = Field(
        default="Cardiovascular Disease Risk Prediction & Intervention Recommendation",
        description="API description"
    )
    api_version: str = Field(default="1.0.0", description="API version")
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, ge=1, le=65535, description="API port")
    debug: bool = Field(default=False, description="Debug mode")

    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Comma-separated list of allowed CORS origins"
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials in CORS")
    cors_allow_methods: str = Field(default="*", description="Allowed HTTP methods")
    cors_allow_headers: str = Field(default="*", description="Allowed HTTP headers")

    # Security Configuration
    api_key_enabled: bool = Field(default=False, description="Enable API key authentication")
    api_keys: str = Field(default="", description="Comma-separated list of valid API keys")
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, ge=1, description="Max requests per minute")

    # Model Paths
    models_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent / "models",
        description="Directory containing trained ML models"
    )
    risk_predictor_filename: str = Field(
        default="risk_predictor.pkl",
        description="Risk predictor model filename"
    )
    intervention_agent_filename: str = Field(
        default="intervention_agent.pkl",
        description="Intervention agent model filename"
    )
    scaler_path: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent / "data" / "processed" / "scaler.pkl",
        description="Path to data scaler"
    )

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )

    # Environment
    environment: str = Field(default="development", description="Environment (development/staging/production)")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str) -> str:
        """Validate CORS origins format."""
        if not v or v.strip() == "":
            raise ValueError("CORS origins cannot be empty. Specify allowed origins.")
        return v

    @field_validator("api_keys", mode="before")
    @classmethod
    def parse_api_keys(cls, v: str) -> str:
        """Validate API keys format."""
        return v

    @field_validator("environment", mode="before")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed = ["development", "staging", "production"]
        if v.lower() not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v.lower()

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def api_keys_list(self) -> List[str]:
        """Get API keys as a list."""
        if not self.api_keys:
            return []
        return [key.strip() for key in self.api_keys.split(",") if key.strip()]

    @property
    def risk_predictor_path(self) -> Path:
        """Get full path to risk predictor model."""
        return self.models_dir / self.risk_predictor_filename

    @property
    def intervention_agent_path(self) -> Path:
        """Get full path to intervention agent model."""
        return self.models_dir / self.intervention_agent_filename

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Dependency for FastAPI to inject settings.

    Returns:
        Settings instance
    """
    return settings
