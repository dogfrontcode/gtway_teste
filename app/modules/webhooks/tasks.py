"""
Celery tasks for webhook processing.
"""
from datetime import datetime
from flask import current_app
from app.extensions import celery, db
from app.models import Transaction, WebhookAttempt, Tenant
from app.utils.webhook_helpers import send_webhook, calculate_next_retry
from app.schemas.webhook_schemas import WebhookPayloadSchema


@celery.task(bind=True, max_retries=5)
def send_tenant_webhook(self, transaction_id: str):
    """
    Celery task to send webhook notification to tenant.
    
    Args:
        transaction_id: Transaction UUID as string
    """
    try:
        # Get transaction
        transaction = Transaction.query.get(transaction_id)
        
        if not transaction:
            current_app.logger.error(f"Transaction not found: {transaction_id}")
            return
        
        tenant = transaction.tenant
        
        # Check if tenant has webhook configured
        if not tenant.webhook_url:
            current_app.logger.info(f"No webhook URL configured for tenant {tenant.slug}")
            return
        
        # Prepare payload
        schema = WebhookPayloadSchema()
        payload = schema.dump({
            'transaction_id': str(transaction.id),
            'txid': transaction.txid,
            'amount': transaction.amount,
            'currency': transaction.currency,
            'status': transaction.status,
            'description': transaction.description,
            'payer_name': transaction.payer_name,
            'payer_document': transaction.payer_document,
            'paid_at': transaction.paid_at,
            'created_at': transaction.created_at
        })
        
        # Get current attempt number
        attempt_count = WebhookAttempt.query.filter_by(
            transaction_id=transaction.id
        ).count() + 1
        
        # Create webhook attempt record
        attempt = WebhookAttempt(
            transaction_id=transaction.id,
            attempt_number=attempt_count,
            url=tenant.webhook_url,
            payload=payload,
            status='pending'
        )
        db.session.add(attempt)
        db.session.commit()
        
        # Send webhook
        result = send_webhook(
            url=tenant.webhook_url,
            payload=payload,
            secret=tenant.webhook_secret
        )
        
        # Update attempt status
        if result['success']:
            attempt.mark_success(
                response_status=result['status_code'],
                response_body=result.get('response_body')
            )
            db.session.commit()
            current_app.logger.info(
                f"Webhook delivered successfully to {tenant.slug} for transaction {transaction.txid}"
            )
        else:
            attempt.mark_failed(
                error_message=result['error'],
                response_status=result.get('status_code'),
                response_body=result.get('response_body')
            )
            
            # Schedule retry if not exceeded max attempts
            max_attempts = current_app.config.get('WEBHOOK_RETRY_MAX_ATTEMPTS', 5)
            
            if attempt_count < max_attempts:
                next_retry = calculate_next_retry(
                    attempt_count,
                    base=current_app.config.get('WEBHOOK_RETRY_BACKOFF_BASE', 2)
                )
                attempt.next_retry_at = next_retry
                db.session.commit()
                
                # Retry with exponential backoff
                retry_seconds = (next_retry - datetime.utcnow()).total_seconds()
                current_app.logger.warning(
                    f"Webhook failed for {tenant.slug}, retrying in {retry_seconds}s "
                    f"(attempt {attempt_count}/{max_attempts})"
                )
                raise self.retry(countdown=int(retry_seconds))
            else:
                db.session.commit()
                current_app.logger.error(
                    f"Webhook delivery failed after {max_attempts} attempts for "
                    f"transaction {transaction.txid}"
                )
        
    except Exception as e:
        current_app.logger.error(f"Error in webhook task: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60)


@celery.task
def retry_failed_webhooks():
    """
    Periodic task to retry failed webhooks that are ready for retry.
    This should be scheduled to run periodically (e.g., every 5 minutes).
    """
    try:
        now = datetime.utcnow()
        
        # Find failed attempts ready for retry
        failed_attempts = WebhookAttempt.query.filter(
            WebhookAttempt.status == 'failed',
            WebhookAttempt.next_retry_at <= now,
            WebhookAttempt.next_retry_at.isnot(None)
        ).all()
        
        for attempt in failed_attempts:
            # Clear next_retry_at to prevent duplicate processing
            attempt.next_retry_at = None
            db.session.commit()
            
            # Schedule webhook retry
            send_tenant_webhook.delay(str(attempt.transaction_id))
        
        if failed_attempts:
            current_app.logger.info(f"Scheduled {len(failed_attempts)} webhook retries")
        
    except Exception as e:
        current_app.logger.error(f"Error in retry_failed_webhooks task: {e}")
