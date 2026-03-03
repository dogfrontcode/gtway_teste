"""
Flask extensions initialization.
Extensions are initialized here and then initialized with the app in the factory.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger
from celery import Celery

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
swagger = Swagger()

# Celery instance (will be configured in factory)
celery = Celery()


def init_celery(app, celery_instance):
    """
    Initialize Celery with Flask app context.
    
    Args:
        app: Flask application instance
        celery_instance: Celery instance to configure
    """
    celery_instance.conf.update(app.config)
    
    class ContextTask(celery_instance.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery_instance.Task = ContextTask
    return celery_instance
