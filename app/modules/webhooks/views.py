"""
Webhook routes/views.
"""
from flask import request, jsonify
from marshmallow import ValidationError
from datetime import datetime
from app.modules.webhooks import webhooks_bp
from app.modules.webhooks.services import WebhookService
from app.schemas.webhook_schemas import BankWebhookSchema
from app.extensions import limiter


@webhooks_bp.route('/bank', methods=['POST'])
@limiter.limit("100 per minute")
def receive_bank_webhook():
    """
    Receive webhook notification from bank/PSP.
    This is a public endpoint that banks will call to notify payment status.
    ---
    tags:
      - Webhooks
    parameters:
      - in: body
        name: body
        required: true
        description: Webhook payload from bank
        schema:
          type: object
          required:
            - txid
            - status
          properties:
            txid:
              type: string
              example: TXN20250302123456ABC
            status:
              type: string
              enum: [paid, cancelled, expired]
              example: paid
            amount:
              type: number
              format: decimal
              example: 100.50
            payer:
              type: object
              properties:
                name:
                  type: string
                document:
                  type: string
            paid_at:
              type: string
              format: date-time
      - in: header
        name: X-Signature
        type: string
        description: Webhook signature for validation
    responses:
      200:
        description: Webhook processed successfully
      400:
        description: Invalid payload
      404:
        description: Transaction not found
    """
    try:
        # Get signature from header
        signature = request.headers.get('X-Signature')
        
        # Validate input
        schema = BankWebhookSchema()
        data = schema.load(request.json, partial=True)
        
        # Extract data
        txid = data['txid']
        status = data['status']
        amount = data.get('amount')
        payer = data.get('payer')
        paid_at_str = data.get('paid_at')
        
        paid_at = None
        if paid_at_str:
            if isinstance(paid_at_str, str):
                paid_at = datetime.fromisoformat(paid_at_str.replace('Z', '+00:00'))
            else:
                paid_at = paid_at_str
        
        # Process webhook
        success, error = WebhookService.process_bank_webhook(
            txid=txid,
            status=status,
            amount=amount,
            payer_info=payer,
            paid_at=paid_at,
            signature=signature
        )
        
        if not success:
            if error == "Transaction not found":
                return jsonify({'error': error}), 404
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'Webhook processed successfully',
            'txid': txid
        }), 200
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    except Exception as e:
        return jsonify({'error': 'Webhook processing failed', 'details': str(e)}), 500


@webhooks_bp.route('/test', methods=['POST'])
def test_webhook():
    """
    Test endpoint to simulate a bank webhook (development only).
    ---
    tags:
      - Webhooks
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - txid
          properties:
            txid:
              type: string
              example: TXN20250302123456ABC
            status:
              type: string
              enum: [paid, cancelled, expired]
              default: paid
    responses:
      200:
        description: Test webhook sent
    """
    try:
        data = request.json
        txid = data.get('txid')
        status = data.get('status', 'paid')
        
        if not txid:
            return jsonify({'error': 'txid is required'}), 400
        
        # Simulate bank webhook with minimal data
        success, error = WebhookService.process_bank_webhook(
            txid=txid,
            status=status,
            payer_info={
                'name': 'Test Payer',
                'document': '12345678900'
            }
        )
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'Test webhook processed',
            'txid': txid,
            'status': status
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Test webhook failed', 'details': str(e)}), 500
