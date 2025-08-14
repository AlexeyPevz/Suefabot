import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Конфигурация Flask приложения"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Telegram
    BOT_TOKEN = os.getenv('BOT_TOKEN', '')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://localhost/suefabot')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Sentry
    SENTRY_DSN = os.getenv('SENTRY_DSN', '')
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Server
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Game Settings
    MATCH_TIMEOUT_SECONDS = int(os.getenv('MATCH_TIMEOUT_SECONDS', 60))
    CHOICE_TIMEOUT_SECONDS = int(os.getenv('CHOICE_TIMEOUT_SECONDS', 10))
    COMMISSION_RATE = float(os.getenv('COMMISSION_RATE', 0.05))
    
    # Game Constants
    CHOICES = ['rock', 'scissors', 'paper']
    WINNING_RULES = {
        'rock': 'scissors',
        'scissors': 'paper',
        'paper': 'rock'
    }