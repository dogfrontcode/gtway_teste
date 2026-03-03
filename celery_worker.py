"""
Celery worker entry point.
Run with: celery -A celery_worker.celery worker --loglevel=info
"""
from app import create_app
from app.extensions import celery

# Create Flask app and initialize Celery
app = create_app()
app.app_context().push()

# Import tasks to register them with Celery
from app.modules.webhooks.tasks import send_tenant_webhook, retry_failed_webhooks

# Configure Celery beat schedule (for periodic tasks)
celery.conf.beat_schedule = {
    'retry-failed-webhooks': {
        'task': 'app.modules.webhooks.tasks.retry_failed_webhooks',
        'schedule': 300.0,  # Run every 5 minutes
    },
}
