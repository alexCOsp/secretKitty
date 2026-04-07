"""Vault file I/O — reads and writes the encrypted vault file.

This module ONLY handles file operations. It does not know how to
encrypt or decrypt — that's crypto.py's job. It receives raw bytes
(salt + Fernet token) and writes them to disk, or reads them back.

File format of vault.enc:
    ┌──────────────────┬───────────────────────────┐
    │  salt (16 bytes)  │  Fernet token (variable)  │
    └──────────────────┴───────────────────────────┘
"""

from pathlib import Path

from src.core.crypto import SALT_LENGTH

# Default vault file location — next to the project root
VAULT_PATH = Path("vault.enc")


def vault_exists(path: Path = VAULT_PATH) -> bool:
    """Check if an encrypted vault file exists on disk."""
    return path.is_file()


def save_vault(salt: bytes, encrypted_data: bytes, path: Path = VAULT_PATH) -> None:
    """Write salt + encrypted data to the vault file.

    Args:
        salt: The 16-byte random salt used for key derivation.
        encrypted_data: The Fernet token (output of crypto.encrypt).
        path: Where to write the file. Defaults to vault.enc.

    Why salt is stored with the data:
        On next login, we need the SAME salt to re-derive the SAME key.
        The salt is not secret — it just needs to be unique per vault.
    """
    path.write_bytes(salt + encrypted_data)


def load_vault(path: Path = VAULT_PATH) -> tuple[bytes, bytes]:
    """Read the vault file and split it into salt and encrypted data.

    Returns:
        A tuple of (salt, encrypted_data):
        - salt: first 16 bytes — pass to derive_key() with the password
        - encrypted_data: remaining bytes — pass to decrypt() with the key

    Raises:
        FileNotFoundError: If the vault file doesn't exist.
        ValueError: If the file is too small to contain a valid vault.
    """
    raw = path.read_bytes()

    if len(raw) < SALT_LENGTH:
        raise ValueError(
            f"Vault file is corrupted: expected at least {SALT_LENGTH} bytes, "
            f"got {len(raw)}"
        )

    salt = raw[:SALT_LENGTH]
    encrypted_data = raw[SALT_LENGTH:]
    return salt, encrypted_data
