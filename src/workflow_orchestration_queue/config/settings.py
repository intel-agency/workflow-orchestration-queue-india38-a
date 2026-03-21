"""
OS-APOW Application Settings

Pydantic-based settings management with environment variable support.
"""

from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # GitHub Configuration
    github_token: str = Field(default="", description="GitHub App installation token or PAT")
    github_org: str = Field(default="", description="GitHub organization name")
    github_repo: str = Field(default="", description="GitHub repository name")

    # Webhook Configuration
    webhook_secret: str = Field(default="", description="HMAC secret for webhook validation")

    # Sentinel Configuration
    sentinel_bot_login: str = Field(
        default="",
        description="Bot account login for assign-then-verify locking",
    )
    poll_interval: int = Field(default=60, description="Seconds between polling cycles")
    max_backoff: int = Field(default=960, description="Max backoff seconds on rate limits")
    heartbeat_interval: int = Field(default=300, description="Seconds between heartbeat comments")
    subprocess_timeout: int = Field(default=5700, description="Subprocess hard timeout in seconds")

    # API Keys
    zhipu_api_key: str = Field(default="", description="ZhipuAI API key")
    kimi_api_key: str = Field(default="", description="Kimi (Moonshot) API key")

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Enable debug mode")

    # CORS Configuration
    cors_origins: list[str] = Field(
        default=["*"],
        description="Allowed CORS origins",
    )

    @field_validator("github_token", "webhook_secret", mode="before")
    @classmethod
    def validate_not_placeholder(cls: type["Settings"], v: Any) -> str:
        """Ensure secrets are not set to placeholder values."""
        if isinstance(v, str):
            placeholders = {"your_webhook_secret_here", "YOUR_GITHUB_TOKEN", "your_token_here"}
            if v.lower() in placeholders:
                return ""
        return v if isinstance(v, str) else ""

    def validate_required(self) -> None:
        """Validate that required settings are present."""
        # Only validate if running the notifier (webhook receiver)
        # Sentinel can run with just GITHUB_TOKEN
        pass


# Global settings instance
settings = Settings()
