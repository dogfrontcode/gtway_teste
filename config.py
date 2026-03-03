"""
Configuration settings for the Payment Gateway application.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # SQLAlchemy (use absolute path for SQLite to avoid "unable to open database file")
    _sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gateway.db')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{_sqlite_path}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Disabled for cleaner output
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000)))
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Celery
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'UTC'
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'redis://localhost:6379/1')
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_HEADERS_ENABLED = True
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Encryption
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'dev-encryption-key-must-be-32-bytes-long!!')
    
    # Bank/PSP Configuration
    DEFAULT_BANK_PROVIDER = os.getenv('DEFAULT_BANK_PROVIDER', 'mock')
    BANK_API_URL = os.getenv('BANK_API_URL', 'https://sandbox.banco.com/api')
    BANK_TIMEOUT = int(os.getenv('BANK_TIMEOUT', 30))
    
    # Webhook Configuration
    WEBHOOK_RETRY_MAX_ATTEMPTS = int(os.getenv('WEBHOOK_RETRY_MAX_ATTEMPTS', 5))
    WEBHOOK_RETRY_BACKOFF_BASE = int(os.getenv('WEBHOOK_RETRY_BACKOFF_BASE', 2))
    WEBHOOK_SIGNATURE_SECRET = os.getenv('WEBHOOK_SIGNATURE_SECRET', 'webhook-secret')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/gateway.log')
    
    # Swagger
    SWAGGER = {
        'title': 'Payment Gateway API',
        'version': '1.0.0',
        'description': 'White Label Payment Gateway - RESTful API Documentation',
        'termsOfService': '',
        'hide_top_bar': False,
        'specs_route': '/swagger/',
    }


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    JWT_CSRF_PROTECT = False  # Disable CSRF for API testing
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
