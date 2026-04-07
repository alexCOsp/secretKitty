"""Cryptographic primitives for the password vault.

This module handles key derivation and encryption/decryption.
The key ONLY lives in memory — it is never written to disk.
"""

import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# ── Constants ───────────────────────────────
SALT_LENGTH = 16  # 16 bytes = 128 bits, minimum for PBKDF2
ITERATIONS = 600_000  # OWASP 2024 minimum for SHA-256
KEY_LENGTH = 32  # Fernet needs exactly 32 bytes before base64


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


# ── Encrypt / Decrypt ───────────────────────


def encrypt(key: bytes, plaintext: str) -> bytes:
    """Encrypt a plaintext string using Fernet.

    What happens inside Fernet.encrypt():
      1. Generate a random 16-byte IV (you never touch this)
      2. Pad the plaintext to a block boundary (PKCS7)
      3. AES-128-CBC encrypt with the IV
      4. HMAC-SHA256 the whole thing (version + timestamp + IV + ciphertext)
      5. Pack it all into one base64 token

    Args:
        key: Fernet key from derive_key() (base64-encoded).
        plaintext: The data to encrypt (e.g., JSON string of vault entries).

    Returns:
        Fernet token (bytes) — contains IV + ciphertext + HMAC, all in one blob.
    """
    f = Fernet(key)
    return f.encrypt(plaintext.encode("utf-8"))


def decrypt(key: bytes, token: bytes) -> str:
    """Decrypt a Fernet token back to the original plaintext string.

    What happens inside Fernet.decrypt():
      1. Decode the base64 token
      2. Verify the HMAC — if tampered, raises InvalidToken BEFORE decrypting
         (this is "authenticated encryption" — you know it wasn't modified)
      3. AES-128-CBC decrypt using the embedded IV
      4. Remove PKCS7 padding
      5. Return the original bytes

    Args:
        key: The same Fernet key used to encrypt.
        token: The encrypted Fernet token from encrypt().

    Returns:
        The original plaintext string.

    Raises:
        InvalidToken: If the key is wrong OR the data was tampered with.
            Fernet intentionally doesn't tell you which — that's a security
            feature. Telling an attacker "wrong key" vs "corrupted data"
            would leak information.
    """
    f = Fernet(key)
    return f.decrypt(token).decode("utf-8")
