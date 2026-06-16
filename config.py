import os
import secrets
from dotenv import load_dotenv

load_dotenv()


def _resolve_secret_key() -> str:
    """Return the Flask secret key without ever using a source-controlled fallback.

    Production must supply SECRET_KEY explicitly; otherwise we fail fast rather
    than sign sessions with a publicly known value. Outside production we mint an
    ephemeral random key so local runs work with zero setup.
    """
    configured_key = os.environ.get('SECRET_KEY')
    if configured_key:
        return configured_key
    if os.environ.get('FLASK_ENV') == 'production':
        raise RuntimeError('SECRET_KEY environment variable must be set in production')
    return secrets.token_hex(32)


class Config:
    """Application configuration"""
    SECRET_KEY = _resolve_secret_key()
    
    # Database - Handle PostgreSQL for Render
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///blackshepherd.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Paystack configuration
    PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY')
    PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
    PAYSTACK_WEBHOOK_SECRET = os.environ.get('PAYSTACK_WEBHOOK_SECRET')
    
    # Site settings
    SITE_NAME = os.environ.get('SITE_NAME', 'Black Shepherd Foundation')
    SITE_URL = os.environ.get('SITE_URL', 'http://localhost:5000')