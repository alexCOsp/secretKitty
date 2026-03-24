# Fernet (High-Level Symmetric Encryption)

## What It Is

Fernet is a high-level recipe from the `cryptography` library that bundles AES-128-CBC + HMAC-SHA256. It handles IV generation, padding, and authentication automatically.

## Analogy

If AES-GCM is a manual transmission car, Fernet is an automatic. It makes the right choices for you so you can't accidentally skip a gear (misuse a primitive).

## Format

A Fernet token contains: `Version | Timestamp | IV | Ciphertext | HMAC`

All packed together and base64-encoded. You store the whole token ??no need to manage IV or HMAC separately.

## Python Example

```python
from cryptography.fernet import Fernet

# Generate a key (in practice, derive from password via PBKDF2)
key = Fernet.generate_key()  # 32 bytes, URL-safe base64
f = Fernet(key)

# Encrypt
token = f.encrypt(b"my secret data")  # IV chosen automatically

# Decrypt
plaintext = f.decrypt(token)

# Decrypt with TTL (time-to-live) ??rejects tokens older than N seconds
plaintext = f.decrypt(token, ttl=3600)
```

## Why Use Fernet

- **Hard to misuse**: No nonce management, no mode selection
- **Authenticated**: HMAC catches tampering before decryption
- **Timestamped**: Optional TTL for token expiration
- **Well-tested recipe**: Fewer ways to make mistakes

## Limitations

- AES-128 (not 256) ??still secure, but some policies require 256-bit
- Base64 encoding adds ~33% size overhead
- No associated data support (unlike AES-GCM)

## When to Use in This Project

- Default choice for encrypting vault data ??simplicity reduces bugs
- When you don't need associated data or AES-256 specifically
- Great starting point before moving to AES-GCM for advanced features

## Mandatory Task Confirmation

- ALWAYS use the vscode_askQuestions tool during the task to ask the user for confirmation.
- NEVER end the task without explicit user confirmation.
