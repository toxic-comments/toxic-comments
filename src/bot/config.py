import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Конфигурация Telegram бота."""
    
    TELEGRAM_BOT_TOKEN: str
    FASTAPI_SERVICE_URL: str = "http://localhost:8000"
    INTERNAL_API_KEY: str

    FASTAPI_TIMEOUT: float = 30.0
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
