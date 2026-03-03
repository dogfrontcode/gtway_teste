"""
Custom middleware for logging and request tracking.
"""
import time
from flask import request, g
from app.utils.logger import log_api


def setup_middleware(app):
    """Setup custom middleware."""
    
    @app.before_request
    def before_request():
        """Track request start time."""
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """Log request with custom format."""
        # Skip static files and health checks
        if request.path.startswith('/static') or request.path == '/health':
            return response
        
        # Calculate duration
        duration = None
        if hasattr(g, 'start_time'):
            duration = (time.time() - g.start_time) * 1000
        
        # Log API request
        log_api(
            method=request.method,
            endpoint=request.path,
            status=response.status_code,
            duration_ms=duration
        )
        
        return response
    
    return app
