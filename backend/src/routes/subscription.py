from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import stripe
import os

subscription_bp = Blueprint('subscription', __name__)

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@subscription_bp.route('/subscription/create-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create a Stripe checkout session for subscription"""
    try:
        data = request.json
        price_id = data.get('price_id', 'price_1234567890')  # Replace with actual Stripe price ID

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url='http://localhost:5173/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:5173/cancel',
            client_reference_id=str(current_user.id),
        )

        return jsonify({'session_id': session.id, 'url': session.url}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscription_bp.route('/subscription/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks for subscription updates"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('stripe-signature')

    try:
        # Verify webhook signature (add endpoint_secret)
        # event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)

        # For demo, assume event is valid
        # Update user subscription status based on event
        return jsonify({'status': 'success'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@subscription_bp.route('/subscription/status', methods=['GET'])
@login_required
def get_subscription_status():
    """Get current user's subscription status"""
    return jsonify({'status': current_user.subscription_status}), 200