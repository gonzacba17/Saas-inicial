"""
Encryption utilities for sensitive data protection.
"""
import os
import sys
import base64
import hashlib
import secrets
import logging
from typing import Optional, bytes
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

def get_backup_encryption_key() -> bytes:
    """
    Get or generate encryption key for backup files.
    Uses BACKUP_ENCRYPTION_KEY environment variable or generates one.
    """
    # Try to get key from environment
    env_key = os.getenv("BACKUP_ENCRYPTION_KEY")
    if env_key:
        try:
            # Decode base64 key from environment
            return base64.urlsafe_b64decode(env_key.encode())
        except Exception as e:
            logger.error(f"Invalid BACKUP_ENCRYPTION_KEY format: {e}")
    
    # Generate new key if not found
    logger.warning("No BACKUP_ENCRYPTION_KEY found - generating new key")
    
    # Use SECRET_KEY as password base for key derivation
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        logger.critical("SECRET_KEY environment variable required for backup encryption")
        sys.exit(1)
    
    # Generate salt (could be stored separately for better security)
    salt = b"saas_backup_salt_2024"  # In production, use random salt and store securely
    
    # Derive encryption key using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 256 bits
        salt=salt,
        iterations=100000,  # Adjust based on performance needs
    )
    
    key = kdf.derive(secret_key.encode())
    
    # Log warning about generated key (don't log the actual key)
    logger.warning(f"Generated new backup encryption key. Set BACKUP_ENCRYPTION_KEY environment variable to: {base64.urlsafe_b64encode(key).decode()}")
    
    return key

def encrypt_backup_data(data: bytes, key: bytes) -> bytes:
    """
    Encrypt backup data using Fernet encryption.
    """
    try:
        # Create Fernet cipher with the key
        fernet_key = base64.urlsafe_b64encode(key)
        cipher = Fernet(fernet_key)
        
        # Encrypt the data
        encrypted_data = cipher.encrypt(data)
        
        logger.info(f"Successfully encrypted backup data ({len(data)} bytes -> {len(encrypted_data)} bytes)")
        return encrypted_data
        
    except Exception as e:
        logger.error(f"Failed to encrypt backup data: {e}")
        raise

def decrypt_backup_data(encrypted_data: bytes, key: bytes) -> bytes:
    """
    Decrypt backup data using Fernet encryption.
    """
    try:
        # Create Fernet cipher with the key
        fernet_key = base64.urlsafe_b64encode(key)
        cipher = Fernet(fernet_key)
        
        # Decrypt the data
        decrypted_data = cipher.decrypt(encrypted_data)
        
        logger.info(f"Successfully decrypted backup data ({len(encrypted_data)} bytes -> {len(decrypted_data)} bytes)")
        return decrypted_data
        
    except Exception as e:
        logger.error(f"Failed to decrypt backup data: {e}")
        raise

def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.
    """
    return secrets.token_urlsafe(length)

def hash_sensitive_data(data: str, salt: Optional[str] = None) -> str:
    """
    Hash sensitive data with SHA-256.
    """
    if salt is None:
        salt = secrets.token_hex(16)
    
    combined = f"{data}{salt}"
    hash_object = hashlib.sha256(combined.encode())
    return hash_object.hexdigest()

def verify_hash(data: str, hashed: str, salt: str) -> bool:
    """
    Verify hashed data matches the original.
    """
    return hash_sensitive_data(data, salt) == hashed