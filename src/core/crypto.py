"""Cryptographic primitives for the password vault.

This module handles key derivation and encryption/decryption.
The key ONLY lives in memory — it is never written to disk.
"""

import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# ── Constants ───────────────────────────────
SALT_LENGTH = 16        # 16 bytes = 128 bits, minimum for PBKDF2
ITERATIONS = 600_000    # OWASP 2024 minimum for SHA-256
KEY_LENGTH = 32         # Fernet needs exactly 32 bytes before base64


def generate_salt() -> bytes:
    """Generate a cryptographically random salt.

    Why os.urandom?
      - It reads from the OS's crypto-secure random source
      - Never use `random.randbytes()` — that's a predictable PRNG
      - Each vault gets its own unique salt
    """
    return os.urandom(SALT_LENGTH)


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a master password and salt.

    How it works:
      1. Encode the password string to UTF-8 bytes
      2. Feed password + salt into PBKDF2 with SHA-256
      3. Repeat the hash 600,000 times (deliberately slow)
      4. Encode the 32-byte result as URL-safe base64 (Fernet's format)

    Args:
        password: The user's master password (plaintext string).
        salt: Random bytes from generate_salt(), stored with the vault.

    Returns:
        A 44-character URL-safe base64-encoded key for Fernet.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=ITERATIONS,
    )

    # derive() returns 32 raw bytes
    raw_key = kdf.derive(password.encode("utf-8"))

    # Fernet expects URL-safe base64 encoding of those 32 bytes
    return base64.urlsafe_b64encode(raw_key)
