from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    app_name: str = Field(os.environ.get('APP_NAME', 'Name'))

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    version: str =  Field(os.environ.get('APP_VERSION', '0.1.0'))
    jwt_secret_key: str = Field(os.environ.get('JWT_SECRET_KEY', 'change-me!'))
    jwt_algorithm: str = Field(os.environ.get('JWT_ALGORITHM', 'HS256'))
    jwt_expiration_minutes: str = Field(os.environ.get('JWT_EXPIRATION_MINUTES', '60'))


@lru_cache
def get_settings() -> Settings:
    return Settings()

print(get_settings().model_dump())

 
