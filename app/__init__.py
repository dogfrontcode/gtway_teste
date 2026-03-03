"""
Flask application factory.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from config import config_by_name
from app.extensions import db, migrate, jwt, cors, limiter, swagger, celery, init_celery


def create_app(config_name: str = None) -> Flask:
    """
    Application factory pattern.
    
    Args:
        config_name: Configuration name (development, testing, production)
        
    Returns:
        Flask application instance
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Setup logging
    setup_logging(app)
    
    # Initialize Celery
    init_celery(app, celery)
    
    # Setup middleware (custom logging)
    from app.middleware import setup_middleware
    setup_middleware(app)
    
    return app


def initialize_extensions(app: Flask):
    """Initialize Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS']
        }
    })
    limiter.init_app(app)
    
    # Swagger reads config from app.config['SWAGGER']
    swagger.init_app(app)


def register_blueprints(app: Flask):
    """Register Flask blueprints."""
    from app.modules.auth import auth_bp
    from app.modules.tenants import tenants_bp
    from app.modules.payments import payments_bp
    from app.modules.webhooks import webhooks_bp
    from app.modules.admin import admin_bp
    from app.modules.products import products_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(tenants_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(webhooks_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(products_bp)
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'name': 'Payment Gateway API',
            'version': '1.0.0',
            'status': 'running',
            'documentation': '/swagger/'
        })
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'}), 200


def register_error_handlers(app: Flask):
    """Register error handlers."""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal server error: {error}')
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled exception: {error}', exc_info=True)
        return jsonify({'error': 'An unexpected error occurred'}), 500
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authorization token is missing'}), 401


def setup_logging(app: Flask):
    """Setup application logging."""
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # File handler
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.info('Payment Gateway startup')


# Create Celery app for worker
def create_celery_app(app: Flask = None):
    """
    Create Celery application.
    
    Args:
        app: Flask application instance
        
    Returns:
        Celery instance
    """
    if app is None:
        app = create_app()
    
    init_celery(app, celery)
    return celery


# Export celery app for worker
celery_app = celery
