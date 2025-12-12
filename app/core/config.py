from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Application configuration sourced from environment variables."""

    app_name: str = Field(default="Spa Manager API", validation_alias="APP_NAME")
    version: str = Field(default="0.1.0", validation_alias="APP_VERSION")
    jwt_secret_key: str = Field(default="change-me!", validation_alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    jwt_expiration_minutes: str = Field(default="60", validation_alias="JWT_EXPIRATION_MINUTES")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        validate_default=True,
    )


def get_settings() -> Settings:
    return Settings()
