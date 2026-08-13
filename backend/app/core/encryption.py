"""
app/core/encryption.py

Symmetric authenticated encryption for application secrets such as OAuth
access tokens and refresh tokens.

Uses Fernet (AES-128 CBC + HMAC-SHA256) from the `cryptography` package.
Every ciphertext includes a timestamp and is HMAC-authenticated, preventing
tampering and replay attacks.

Security requirements:
  - Encryption key is loaded exclusively from ENCRYPTION_KEY env var.
  - Keys are NEVER hardcoded or logged.
  - Plaintext values are NEVER logged.
  - A missing or invalid ENCRYPTION_KEY raises EncryptionConfigError at call time.
  - Decryption failures raise EncryptionError, never revealing key or plaintext details.

Usage:
    from app.core.encryption import encrypt_secret, decrypt_secret

    ciphertext = encrypt_secret("my-oauth-token")
    plaintext  = decrypt_secret(ciphertext)
"""
import logging

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings

logger = logging.getLogger(__name__)


class EncryptionConfigError(Exception):
    """Raised when the encryption key is missing or invalid."""


class EncryptionError(Exception):
    """Raised when encryption or decryption fails."""


def _get_fernet() -> Fernet:
    """
    Construct a Fernet instance from the environment-configured key.

    Raises:
        EncryptionConfigError: If ENCRYPTION_KEY is absent or not a valid Fernet key.
    """
    key = settings.ENCRYPTION_KEY
    if not key:
        raise EncryptionConfigError(
            "ENCRYPTION_KEY is not configured. "
            "Set it in your .env file. "
            "Generate a key with: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    try:
        return Fernet(key.encode() if isinstance(key, str) else key)
    except Exception as exc:
        raise EncryptionConfigError(
            "ENCRYPTION_KEY is not a valid Fernet key."
        ) from exc


def encrypt_secret(plaintext: str) -> str:
    """
    Encrypt a plaintext secret using Fernet symmetric authenticated encryption.

    The encrypted value is safe to store in the database. It is opaque,
    authenticated, and cannot be decrypted without the correct ENCRYPTION_KEY.

    Args:
        plaintext: The secret string to encrypt (e.g. an OAuth access token).

    Returns:
        A URL-safe base64-encoded ciphertext string.

    Raises:
        EncryptionConfigError: If ENCRYPTION_KEY is not configured or invalid.
        EncryptionError:       If encryption fails for any other reason.
    """
    # NOTE: Do NOT log plaintext here or in callers.
    fernet = _get_fernet()
    try:
        ciphertext = fernet.encrypt(plaintext.encode("utf-8"))
        return ciphertext.decode("utf-8")
    except EncryptionConfigError:
        raise
    except Exception as exc:
        logger.error("Token encryption failed")  # no plaintext in log
        raise EncryptionError("Failed to encrypt secret.") from exc


def decrypt_secret(ciphertext: str) -> str:
    """
    Decrypt a Fernet-encrypted ciphertext back to its original plaintext.

    This function is intended ONLY for trusted internal usage (e.g. making an
    authenticated API call to an external service). It must NEVER be called
    as part of an HTTP response path.

    Args:
        ciphertext: The encrypted string returned by encrypt_secret().

    Returns:
        The original plaintext string.

    Raises:
        EncryptionConfigError: If ENCRYPTION_KEY is not configured or invalid.
        EncryptionError:       If decryption fails (wrong key, tampered data, etc.).
    """
    fernet = _get_fernet()
    try:
        plaintext_bytes = fernet.decrypt(ciphertext.encode("utf-8"))
        return plaintext_bytes.decode("utf-8")
    except EncryptionConfigError:
        raise
    except InvalidToken as exc:
        logger.warning("Token decryption failed: invalid token or wrong key")
        raise EncryptionError("Failed to decrypt secret: invalid token or key.") from exc
    except Exception as exc:
        logger.error("Token decryption failed unexpectedly")  # no ciphertext in log
        raise EncryptionError("Failed to decrypt secret.") from exc
