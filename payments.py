import requests
import hashlib
import hmac
import time
from config import Config
from flask import current_app

def initialize_paystack_payment(transaction):
    """Initialize payment with Paystack using direct HTTP requests"""
    try:
        # Convert amount to kobo (Paystack uses kobo for NGN)
        amount_in_kobo = int(transaction.amount * 100)
        
        # Generate unique reference
        reference = f'BSF_{transaction.id}_{int(time.time())}'
        
        # Prepare payload
        payload = {
            'email': 'donor@blackshepherd.org',  # Anonymous email
            'amount': amount_in_kobo,
            'currency': transaction.currency,
            'reference': reference,
            'callback_url': f'{Config.SITE_URL}/paystack/callback',
            'metadata': {
                'campaign_id': transaction.campaign_id,
                'transaction_db_id': transaction.id,
                'campaign_title': transaction.campaign.title
            }
        }
        
        # Set headers with authorization
        headers = {
            'Authorization': f'Bearer {Config.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Make request to Paystack API
        response = requests.post(
            'https://api.paystack.co/transaction/initialize',
            json=payload,
            headers=headers,
            timeout=30
        )
        
        # Parse response
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status'):
                current_app.logger.info(f"Paystack payment initialized: {reference}")
                return {
                    'success': True,
                    'transaction_id': reference,
                    'method': 'paystack',
                    'redirect_url': data['data']['authorization_url']
                }
            else:
                current_app.logger.error(f"Paystack initialization failed: {data.get('message', 'Unknown error')}")
                return {
                    'success': False,
                    'error': data.get('message', 'Payment initialization failed')
                }
        else:
            current_app.logger.error(f"Paystack API error: HTTP {response.status_code}")
            return {
                'success': False,
                'error': f'Payment service error (HTTP {response.status_code})'
            }
            
    except requests.exceptions.Timeout:
        current_app.logger.error("Paystack API timeout")
        return {
            'success': False,
            'error': 'Payment service timeout. Please try again.'
        }
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Paystack request error: {str(e)}")
        return {
            'success': False,
            'error': 'Payment service unavailable. Please try again.'
        }
    except Exception as e:
        current_app.logger.error(f"Paystack payment error: {str(e)}")
        return {
            'success': False,
            'error': f'Payment processing error: {str(e)}'
        }

def verify_paystack_payment(reference):
    """Verify Paystack payment using direct HTTP requests"""
    try:
        # Set headers with authorization
        headers = {
            'Authorization': f'Bearer {Config.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Make request to verify transaction
        response = requests.get(
            f'https://api.paystack.co/transaction/verify/{reference}',
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') and data['data']['status'] == 'success':
                # Convert amount back from kobo to main currency
                amount = data['data']['amount'] / 100
                
                return {
                    'success': True,
                    'reference': reference,
                    'amount': amount,
                    'currency': data['data']['currency'],
                    'status': data['data']['status'],
                    'transaction_db_id': data['data']['metadata'].get('transaction_db_id'),
                    'campaign_id': data['data']['metadata'].get('campaign_id')
                }
            else:
                return {
                    'success': False,
                    'error': 'Payment was not successful'
                }
        else:
            current_app.logger.error(f"Paystack verify API error: HTTP {response.status_code}")
            return {
                'success': False,
                'error': 'Payment verification failed'
            }
            
    except requests.exceptions.Timeout:
        current_app.logger.error("Paystack verify API timeout")
        return {
            'success': False,
            'error': 'Payment verification timeout'
        }
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Paystack verify request error: {str(e)}")
        return {
            'success': False,
            'error': 'Payment verification failed'
        }
    except Exception as e:
        current_app.logger.error(f"Paystack verification error: {str(e)}")
        return {
            'success': False,
            'error': f'Payment verification failed: {str(e)}'
        }

def test_paystack_connection():
    """Test Paystack API connection using direct HTTP requests"""
    try:
        # Test by fetching banks list
        headers = {
            'Authorization': f'Bearer {Config.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            'https://api.paystack.co/bank',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status'):
                banks_count = len(data.get('data', []))
                return {
                    'success': True,
                    'message': f'Paystack connected successfully. Found {banks_count} banks.'
                }
            else:
                return {
                    'success': False,
                    'message': 'Paystack API returned error'
                }
        else:
            return {
                'success': False,
                'message': f'Paystack connection failed: HTTP {response.status_code}'
            }
            
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'message': 'Paystack connection timeout'
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'message': f'Paystack connection failed: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Paystack connection failed: {str(e)}'
        }

def handle_paystack_webhook(request):
    """Handle Paystack webhook notifications with signature verification"""
    try:
        # Get raw body for signature verification
        payload = request.get_data()
        signature = request.headers.get('X-Paystack-Signature')
        
        # Verify webhook signature (optional but recommended for production)
        if hasattr(Config, 'PAYSTACK_WEBHOOK_SECRET') and Config.PAYSTACK_WEBHOOK_SECRET:
            expected_signature = hmac.new(
                Config.PAYSTACK_WEBHOOK_SECRET.encode('utf-8'),
                payload,
                hashlib.sha512
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                current_app.logger.warning("Invalid webhook signature")
                return {'success': False, 'error': 'Invalid signature'}
        
        # Parse JSON data
        data = request.get_json()
        
        if data and data.get('event') == 'charge.success':
            charge_data = data.get('data', {})
            reference = charge_data.get('reference')
            
            if reference and charge_data.get('status') == 'success':
                # Extract metadata
                metadata = charge_data.get('metadata', {})
                
                return {
                    'success': True,
                    'reference': reference,
                    'transaction_db_id': metadata.get('transaction_db_id'),
                    'amount': charge_data.get('amount', 0) / 100,  # Convert from kobo
                    'campaign_id': metadata.get('campaign_id')
                }
        
        return {'success': False, 'error': 'Unhandled webhook event'}
        
    except Exception as e:
        current_app.logger.error(f"Paystack webhook error: {str(e)}")
        return {'success': False, 'error': str(e)}

def verify_webhook_signature(payload, signature, secret):
    """Verify webhook signature for security"""
    try:
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha512
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)
    except Exception:
        return False

# Currency configurations for Paystack
SUPPORTED_CURRENCIES = [
    ('NGN', '₦ Nigerian Naira'),
    ('USD', '$ US Dollar'),
    ('GHS', 'GH₵ Ghanaian Cedi'),
    ('ZAR', 'R South African Rand'),
    ('KES', 'KSh Kenyan Shilling')
]

def get_currency_symbol(currency_code):
    """Get currency symbol for display"""
    symbols = {
        'NGN': '₦',
        'USD': '$',
        'GHS': 'GH₵',
        'ZAR': 'R',
        'KES': 'KSh',
        'EUR': '€',
        'GBP': '£'
    }
    return symbols.get(currency_code, currency_code)

def format_amount(amount, currency):
    """Format amount with proper currency symbol"""
    symbol = get_currency_symbol(currency)
    return f"{symbol}{amount:,.2f}"

def get_paystack_fees(amount, currency='NGN'):
    """Calculate Paystack transaction fees for reference"""
    if currency == 'NGN':
        # Paystack fees for NGN: 1.5% + ₦100 (capped at ₦2,000)
        fee = (amount * 0.015) + 100
        return min(fee, 2000)
    else:
        # International cards: 3.9%
        return amount * 0.039