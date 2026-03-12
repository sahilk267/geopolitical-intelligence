"""
Encryption Utility for API Key Storage
Uses Fernet symmetric encryption to protect sensitive keys at rest in the database.
"""
import os
import base64
import logging
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


def _get_or_create_encryption_key() -> bytes:
    """
    Get the encryption key from the ENCRYPTION_KEY env var.
    If not set, generate one and log a warning.
    In production, ENCRYPTION_KEY MUST be set as an environment variable.
    """
    key = os.environ.get("ENCRYPTION_KEY")
    if key:
        return key.encode()
    
    # Fallback: derive a key from SECRET_KEY (not ideal, but functional)
    from app.core.config import settings
    secret = settings.SECRET_KEY
    # Pad or hash the secret to get a valid 32-byte Fernet key
    padded = (secret * 3)[:32]
    key_bytes = base64.urlsafe_b64encode(padded.encode())
    logger.warning(
        "ENCRYPTION_KEY not set in environment. Using derived key from SECRET_KEY. "
        "Set ENCRYPTION_KEY in .env for production use."
    )
    return key_bytes


def _get_fernet() -> Fernet:
    """Get a Fernet instance with the current encryption key."""
    return Fernet(_get_or_create_encryption_key())


def encrypt_value(plaintext: str) -> str:
    """
    Encrypt a plaintext string and return a base64-encoded ciphertext.
    Returns the encrypted string prefixed with 'enc:' to distinguish
    from legacy plaintext values.
    """
    if not plaintext:
        return plaintext
    
    f = _get_fernet()
    encrypted = f.encrypt(plaintext.encode())
    return f"enc:{encrypted.decode()}"


def decrypt_value(stored_value: str) -> str:
    """
    Decrypt a stored value. If the value doesn't have the 'enc:' prefix,
    it's a legacy plaintext value and is returned as-is.
    """
    if not stored_value:
        return stored_value
    
    # Legacy plaintext values don't have the prefix
    if not stored_value.startswith("enc:"):
        return stored_value
    
    try:
        f = _get_fernet()
        ciphertext = stored_value[4:]  # Remove 'enc:' prefix
        decrypted = f.decrypt(ciphertext.encode())
        return decrypted.decode()
    except InvalidToken:
        logger.error("Failed to decrypt value — encryption key may have changed.")
        return ""
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        return ""


def mask_key(key_value: str) -> str:
    """Create a masked display version of an API key."""
    if not key_value or len(key_value) <= 8:
        return "****"
    return f"{key_value[:4]}...{key_value[-4:]}"
