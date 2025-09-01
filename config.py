import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///blackshepherd.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Paystack configuration
    PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY')
    PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
    PAYSTACK_WEBHOOK_SECRET = os.environ.get('PAYSTACK_WEBHOOK_SECRET')  # Added for webhook security
    
    # Site settings
    SITE_NAME = os.environ.get('SITE_NAME', 'Black Shepherd Foundation')
    SITE_URL = os.environ.get('SITE_URL', 'http://localhost:5000')