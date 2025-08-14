from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Telegram Bot
    bot_token: str = Field(..., env="BOT_TOKEN")
    webapp_url: str = Field(..., env="WEBAPP_URL")
    
    # Backend API
    api_url: str = Field("http://localhost:5000", env="API_URL")
    
    # Redis
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    
    # PostgreSQL
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Environment
    environment: str = Field("development", env="ENVIRONMENT")
    
    # Webhook
    webhook_host: str = Field("", env="WEBHOOK_HOST")
    webhook_path: str = Field("/webhook", env="WEBHOOK_PATH")
    webhook_port: int = Field(8443, env="WEBHOOK_PORT")
    
    # Game settings
    max_free_games_per_month: int = 10
    match_timeout_seconds: int = 60
    choice_timeout_seconds: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Создаем глобальный экземпляр настроек
settings = Settings()