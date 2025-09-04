import requests
import hashlib
import hmac
import time
import json
from config import Config
from flask import current_app

def initialize_paystack_payment(donation_data):
    """Initialize payment with Paystack using direct HTTP requests"""
    try:
        # Convert amount to kobo (Paystack uses kobo for NGN)
        if donation_data['currency'] == 'NGN':
            amount_in_minor = int(donation_data['amount'] * 100)  # Convert to kobo
        else:
            amount_in_minor = int(donation_data['amount'] * 100)  # Convert to cents
        
        # Generate unique reference
        timestamp = int(time.time())
        reference = f'BSF_{donation_data["campaign_id"]}_{timestamp}'
        
        # Prepare payload for Paystack API
        payload = {
            'email': donation_data['email'],
            'amount': amount_in_minor,
            'currency': donation_data['currency'],
            'reference': reference,
            'callback_url': donation_data['callback_url'],
            'metadata': {
                'campaign_id': donation_data['campaign_id'],
                'campaign_title': donation_data['campaign_title'],
                'original_amount': donation_data['amount'],
                'donor_type': 'anonymous'
            }
        }
        
        # Set headers with authorization
        headers = {
            'Authorization': f'Bearer {Config.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        current_app.logger.info(f"Initializing Paystack payment for reference: {reference}")
        
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
                current_app.logger.info(f"Paystack payment initialized successfully: {reference}")
                return {
                    'success': True,
                    'reference': reference,
                    'authorization_url': data['data']['authorization_url'],
                    'access_code': data['data']['access_code']
                }
            else:
                error_message = data.get('message', 'Payment initialization failed')
                current_app.logger.error(f"Paystack initialization failed: {error_message}")
                return {
                    'success': False,
                    'error': error_message
                }
        else:
            current_app.logger.error(f"Paystack API error: HTTP {response.status_code}")
            try:
                error_data = response.json()
                error_message = error_data.get('message', f'HTTP {response.status_code} error')
            except:
                error_message = f'HTTP {response.status_code} error'
            
            return {
                'success': False,
                'error': error_message
            }
            
    except requests.exceptions.Timeout:
        current_app.logger.error("Paystack API timeout during initialization")
        return {
            'success': False,
            'error': 'Payment service timeout. Please try again.'
        }
    except requests.exceptions.ConnectionError:
        current_app.logger.error("Paystack API connection error during initialization")
        return {
            'success': False,
            'error': 'Unable to connect to payment service. Please try again.'
        }
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Paystack request error during initialization: {str(e)}")
        return {
            'success': False,
            'error': 'Payment service error. Please try again.'
        }
    except Exception as e:
        current_app.logger.error(f"Unexpected error during payment initialization: {str(e)}")
        return {
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }

def verify_paystack_payment(reference):
    """Verify Paystack payment using direct HTTP requests"""
    try:
        # Set headers with authorization
        headers = {
            'Authorization': f'Bearer {Config.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        current_app.logger.info(f"Verifying Paystack payment for reference: {reference}")
        
        # Make request to verify transaction
        response = requests.get(
            f'https://api.paystack.co/transaction/verify/{reference}',
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') and data['data']['status'] == 'success':
                # Convert amount back from minor currency to major
                if data['data']['currency'] == 'NGN':
                    amount = data['data']['amount'] / 100  # Convert from kobo
                else:
                    amount = data['data']['amount'] / 100  # Convert from cents
                
                metadata = data['data'].get('metadata', {})
                
                current_app.logger.info(f"Payment verification successful: {reference}")
                
                return {
                    'success': True,
                    'reference': reference,
                    'amount': amount,
                    'currency': data['data']['currency'],
                    'status': data['data']['status'],
                    'campaign_id': metadata.get('campaign_id'),
                    'campaign_title': metadata.get('campaign_title'),
                    'transaction_date': data['data']['transaction_date'],
                    'customer_email': data['data']['customer']['email']
                }
            else:
                transaction_status = data['data'].get('status', 'unknown')
                current_app.logger.warning(f"Payment verification failed - status: {transaction_status}")
                return {
                    'success': False,
                    'error': f'Payment was not successful. Status: {transaction_status}'
                }
        else:
            current_app.logger.error(f"Paystack verify API error: HTTP {response.status_code}")
            try:
                error_data = response.json()
                error_message = error_data.get('message', 'Payment verification failed')
            except:
                error_message = 'Payment verification failed'
            
            return {
                'success': False,
                'error': error_message
            }
            
    except requests.exceptions.Timeout:
        current_app.logger.error("Paystack API timeout during verification")
        return {
            'success': False,
            'error': 'Payment verification timeout. Please contact support.'
        }
    except requests.exceptions.ConnectionError:
        current_app.logger.error("Paystack API connection error during verification")
        return {
            'success': False,
            'error': 'Unable to verify payment. Please contact support.'
        }
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Paystack verify request error: {str(e)}")
        return {
            'success': False,
            'error': 'Payment verification failed. Please contact support.'
        }
    except Exception as e:
        current_app.logger.error(f"Unexpected error during payment verification: {str(e)}")
        return {
            'success': False,
            'error': 'Payment verification error. Please contact support.'
        }

def test_paystack_connection():
    """Test Paystack API connection using direct HTTP requests"""
    try:
        # Test by fetching banks list (simple API call)
        headers = {
            'Authorization': f'Bearer {Config.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
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
                    'message': f'Paystack connected successfully. Found {banks_count} supported banks.'
                }
            else:
                return {
                    'success': False,
                    'message': f'Paystack API returned error: {data.get("message", "Unknown error")}'
                }
        else:
            try:
                error_data = response.json()
                error_message = error_data.get('message', f'HTTP {response.status_code}')
            except:
                error_message = f'HTTP {response.status_code}'
            
            return {
                'success': False,
                'message': f'Paystack connection failed: {error_message}'
            }
            
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'message': 'Paystack connection timeout'
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'message': 'Unable to connect to Paystack. Check internet connection.'
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'message': f'Paystack connection error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Unexpected connection error: {str(e)}'
        }

def handle_paystack_webhook(request):
    """Handle Paystack webhook notifications with signature verification"""
    try:
        # Get raw body for signature verification
        payload = request.get_data()
        signature = request.headers.get('X-Paystack-Signature')
        
        # Verify webhook signature if webhook secret is configured
        if hasattr(Config, 'PAYSTACK_WEBHOOK_SECRET') and Config.PAYSTACK_WEBHOOK_SECRET:
            if not verify_webhook_signature(payload, signature, Config.PAYSTACK_WEBHOOK_SECRET):
                current_app.logger.warning("Invalid Paystack webhook signature")
                return {'success': False, 'error': 'Invalid signature'}
        
        # Parse JSON data
        data = request.get_json()
        
        if data and data.get('event') == 'charge.success':
            charge_data = data.get('data', {})
            reference = charge_data.get('reference')
            
            if reference and charge_data.get('status') == 'success':
                # Convert amount from minor currency
                if charge_data.get('currency') == 'NGN':
                    amount = charge_data.get('amount', 0) / 100  # Convert from kobo
                else:
                    amount = charge_data.get('amount', 0) / 100  # Convert from cents
                
                metadata = charge_data.get('metadata', {})
                
                current_app.logger.info(f"Webhook processed successfully for reference: {reference}")
                
                return {
                    'success': True,
                    'reference': reference,
                    'amount': amount,
                    'currency': charge_data.get('currency'),
                    'campaign_id': metadata.get('campaign_id'),
                    'campaign_title': metadata.get('campaign_title')
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
    except Exception as e:
        current_app.logger.error(f"Webhook signature verification error: {str(e)}")
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

# Helper function to validate Paystack configuration
def validate_paystack_config():
    """Validate that Paystack configuration is properly set"""
    errors = []
    
    if not Config.PAYSTACK_SECRET_KEY:
        errors.append("PAYSTACK_SECRET_KEY is not configured")
    elif not Config.PAYSTACK_SECRET_KEY.startswith('sk_'):
        errors.append("PAYSTACK_SECRET_KEY appears to be invalid (should start with 'sk_')")
    
    if not Config.PAYSTACK_PUBLIC_KEY:
        errors.append("PAYSTACK_PUBLIC_KEY is not configured")
    elif not Config.PAYSTACK_PUBLIC_KEY.startswith('pk_'):
        errors.append("PAYSTACK_PUBLIC_KEY appears to be invalid (should start with 'pk_')")
    
    return errors

# Test function to validate configuration on startup
def startup_validation():
    """Validate Paystack configuration on application startup"""
    errors = validate_paystack_config()
    
    if errors:
        print("⚠️ Paystack Configuration Issues:")
        for error in errors:
            print(f"   - {error}")
        print("   Please check your .env file and ensure Paystack keys are properly configured.")
        return False
    
    print("✅ Paystack configuration validated successfully")
    return True 