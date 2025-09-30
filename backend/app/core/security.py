"""
Security module for handling sensitive data and credentials securely.
"""
import os
import sys
import urllib.parse
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def get_database_url() -> str:
    """
    Get database URL from environment variables with security validation.
    Raises SystemExit if required credentials are missing in production.
    """
    # Check if DATABASE_URL is directly provided
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return _ensure_utf8_encoding(database_url)
    
    # Build from individual components
    postgres_user = os.getenv("POSTGRES_USER")
    postgres_password = os.getenv("POSTGRES_PASSWORD")
    postgres_host = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port = os.getenv("POSTGRES_PORT", "5432")
    postgres_db = os.getenv("POSTGRES_DB")
    
    # Security validation - fail fast in production
    environment = os.getenv("ENVIRONMENT", "development")
    if environment == "production":
        missing_vars = []
        if not postgres_user:
            missing_vars.append("POSTGRES_USER")
        if not postgres_password:
            missing_vars.append("POSTGRES_PASSWORD")
        if not postgres_db:
            missing_vars.append("POSTGRES_DB")
            
        if missing_vars:
            logger.critical(f"Missing required database environment variables in production: {', '.join(missing_vars)}")
            sys.exit(1)
    
    # Use safe defaults for development only
    if not postgres_user:
        postgres_user = "postgres"
        logger.warning("Using default postgres user for development")
    
    if not postgres_password:
        logger.critical("POSTGRES_PASSWORD environment variable is required")
        sys.exit(1)
    
    if not postgres_db:
        postgres_db = "saas_cafeterias"
        logger.warning("Using default database name for development")
    
    # URL encode components to handle special characters
    try:
        encoded_user = urllib.parse.quote_plus(str(postgres_user))
        encoded_password = urllib.parse.quote_plus(str(postgres_password))
        encoded_host = urllib.parse.quote_plus(str(postgres_host))
        encoded_db = urllib.parse.quote_plus(str(postgres_db))
        
        # Build URL with UTF-8 encoding
        database_url = f"postgresql://{encoded_user}:{encoded_password}@{encoded_host}:{postgres_port}/{encoded_db}?client_encoding=utf8"
        
        return database_url
        
    except Exception as e:
        logger.critical(f"Error building database URL: {str(e)}")
        sys.exit(1)

def _ensure_utf8_encoding(url: str) -> str:
    """Ensure database URL has proper UTF-8 encoding parameters."""
    if url.startswith('postgresql'):
        if 'client_encoding=utf8' not in url:
            separator = '&' if '?' in url else '?'
            url += f"{separator}client_encoding=utf8"
    return url

def validate_required_secrets() -> bool:
    """
    Validate that all required secrets are present for the current environment.
    Returns True if all required secrets are present, False otherwise.
    """
    environment = os.getenv("ENVIRONMENT", "development")
    required_secrets = []
    
    # Always required
    if not os.getenv("SECRET_KEY") or os.getenv("SECRET_KEY") in ["change-this-in-production", "dev-secret-key-change-in-production-12345"]:
        required_secrets.append("SECRET_KEY (must be strong and unique)")
    
    # Production-specific requirements
    if environment == "production":
        if not os.getenv("POSTGRES_PASSWORD"):
            required_secrets.append("POSTGRES_PASSWORD")
        
        # Payment processing
        if not os.getenv("MERCADOPAGO_ACCESS_TOKEN"):
            logger.warning("MERCADOPAGO_ACCESS_TOKEN not set - payment features will be disabled")
        
        # Webhook security
        if not os.getenv("MERCADOPAGO_WEBHOOK_SECRET"):
            required_secrets.append("MERCADOPAGO_WEBHOOK_SECRET (required for payment security)")
    
    if required_secrets:
        logger.error(f"Missing required secrets for {environment} environment:")
        for secret in required_secrets:
            logger.error(f"  - {secret}")
        return False
    
    logger.info(f"All required secrets present for {environment} environment")
    return True

def get_webhook_secret() -> Optional[str]:
    """
    Get webhook secret with validation.
    Returns None if not configured, but logs appropriate warnings.
    """
    webhook_secret = os.getenv("MERCADOPAGO_WEBHOOK_SECRET")
    environment = os.getenv("ENVIRONMENT", "development")
    
    if not webhook_secret:
        if environment == "production":
            logger.critical("MERCADOPAGO_WEBHOOK_SECRET is required in production")
            return None
        else:
            logger.warning("MERCADOPAGO_WEBHOOK_SECRET not configured - webhook validation disabled")
            return None
    
    if len(webhook_secret) < 32:
        logger.warning("Webhook secret is too short - should be at least 32 characters")
    
    return webhook_secret