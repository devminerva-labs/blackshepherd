#!/usr/bin/env python3
"""
Quick test script to verify Paystack direct HTTP integration works
Run this after updating your .env file with Paystack credentials
"""
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

def test_paystack_connection():
    """Test basic API connection"""
    secret_key = os.environ.get('PAYSTACK_SECRET_KEY')
    
    if not secret_key:
        print("❌ PAYSTACK_SECRET_KEY not found in environment")
        return False
    
    print("🔑 Testing Paystack connection...")
    
    headers = {
        'Authorization': f'Bearer {secret_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            'https://api.paystack.co/bank',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status'):
                banks_count = len(data.get('data', []))
                print(f"✅ Paystack connected successfully!")
                print(f"📊 Found {banks_count} supported banks")
                return True
            else:
                print(f"❌ Paystack API error: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Connection timeout")
        return False
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False

def test_payment_initialization():
    """Test payment initialization (doesn't actually charge)"""
    secret_key = os.environ.get('PAYSTACK_SECRET_KEY')
    site_url = os.environ.get('SITE_URL', 'http://localhost:5000')
    webhook_secret = os.environ.get('PAYSTACK_WEBHOOK_SECRET')
    
    if not secret_key:
        print("❌ PAYSTACK_SECRET_KEY not found")
        return False
    
    print("\n💳 Testing payment initialization...")
    print(f"🔐 Secret Key: {secret_key[:15]}...{secret_key[-10:]}")
    print(f"🪝 Webhook Secret: {webhook_secret if webhook_secret else 'Not set'}")
    
    # Generate unique reference
    reference = f'BSF_TEST_{int(time.time())}'
    
    payload = {
        'email': 'test@blackshepherd.org',
        'amount': 500000,  # ₦5,000 in kobo
        'currency': 'NGN',
        'reference': reference,
        'callback_url': f'{site_url}/paystack/callback',
        'metadata': {
            'campaign_id': 1,
            'transaction_db_id': 999,
            'campaign_title': 'Test Campaign'
        }
    }
    
    headers = {
        'Authorization': f'Bearer {secret_key}',
        'Content-Type': 'application/json'
    }
    
    print(f"📝 Reference: {reference}")
    print(f"💰 Amount: ₦5,000")
    print(f"🔗 Callback URL: {payload['callback_url']}")
    
    try:
        response = requests.post(
            'https://api.paystack.co/transaction/initialize',
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status'):
                print("✅ Payment initialization successful!")
                print(f"🔗 Payment URL: {data['data']['authorization_url']}")
                print(f"📝 Reference: {data['data']['reference']}")
                return True
            else:
                print(f"❌ Initialization failed: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Initialization error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Black Shepherd Foundation - Paystack Direct HTTP Test")
    print("=" * 50)
    
    # Show environment status
    print(f"🌍 Environment Variables:")
    print(f"   PAYSTACK_PUBLIC_KEY: {'✅ Set' if os.environ.get('PAYSTACK_PUBLIC_KEY') else '❌ Not Set'}")
    print(f"   PAYSTACK_SECRET_KEY: {'✅ Set' if os.environ.get('PAYSTACK_SECRET_KEY') else '❌ Not Set'}")
    print(f"   PAYSTACK_WEBHOOK_SECRET: {'✅ Set' if os.environ.get('PAYSTACK_WEBHOOK_SECRET') else '❌ Not Set'}")
    print(f"   SITE_URL: {os.environ.get('SITE_URL', 'Not Set')}")
    
    # Test 1: Basic connection
    connection_ok = test_paystack_connection()
    
    # Test 2: Payment initialization  
    if connection_ok:
        payment_ok = test_payment_initialization()
    else:
        payment_ok = False
    
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY:")
    print(f"   Connection Test: {'✅ PASSED' if connection_ok else '❌ FAILED'}")
    print(f"   Payment Test: {'✅ PASSED' if payment_ok else '❌ FAILED'}")
    
    if connection_ok and payment_ok:
        print("\n🎉 All tests passed! Paystack integration is ready.")
        print("💡 Next steps:")
        print("   1. Run your Flask app: python app.py")
        print("   2. Visit http://localhost:5000")
        print("   3. Add test campaigns and try donations")
    else:
        print("\n⚠️  Some tests failed. Check your Paystack credentials in .env file")
        print("💡 Make sure you have:")
        print("   - Valid PAYSTACK_SECRET_KEY (starts with sk_test_ or sk_live_)")
        print("   - Valid PAYSTACK_PUBLIC_KEY (starts with pk_test_ or pk_live_)")
        print("   - PAYSTACK_WEBHOOK_SECRET (get from Paystack dashboard)")
        print("   - Internet connection for API calls")
        
        if not connection_ok:
            print("\n🔧 Connection failed - check your secret key")
        if connection_ok and not payment_ok:
            print("\n🔧 Payment initialization failed - possible account verification issue")

if __name__ == '__main__':
    main()