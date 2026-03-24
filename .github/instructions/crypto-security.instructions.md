---
description: "Use when working with cryptography, encryption, key derivation, hashing, password storage, secrets, or security-sensitive code. Covers safe crypto patterns and common vulnerabilities."
applyTo: "src/core/**"
---

# Cryptography & Security Rules

## Library

- Use the `cryptography` library exclusively for all crypto operations
- NEVER roll custom crypto ??no hand-written AES, no XOR "encryption"
- Prefer high-level APIs (Fernet) unless low-level is explicitly needed

## Key Derivation

- PBKDF2: minimum 600,000 iterations (OWASP 2024 recommendation)
- Argon2id: preferred if available (`argon2-cffi` package)
- Salt: minimum 16 bytes from `os.urandom()`, unique per derivation
- NEVER reuse salts across different passwords/keys

## Encryption

- Use authenticated encryption only: AES-GCM or Fernet
- AES-GCM nonces: 12 bytes from `os.urandom()`, NEVER reuse with same key
- Fernet handles nonce/IV internally ??prefer for simplicity
- NEVER use ECB mode or unauthenticated CBC

## Random Generation

- Use `secrets` module for tokens, passwords, IDs
- Use `os.urandom()` for cryptographic bytes
- NEVER use `random` module for anything security-related
- `random` is a PRNG seeded predictably ??not cryptographically secure

## Sensitive Data

- Zeroize byte arrays after use: `sensitive_bytes[:] = b'\x00' * len(sensitive_bytes)`
- NEVER log passwords, keys, or plaintext secrets
- NEVER hardcode keys, passwords, or salts in source code
- Use `getpass.getpass()` for interactive password input

## Storage

- Store encrypted data + salt + nonce together (but never the key)
- Use SQLite parameterized queries to prevent SQL injection
- Database file permissions: owner-only read/write

## Common Mistakes to Flag

- Using `hashlib` alone for password storage (no salt, no iterations)
- Comparing hashes with `==` instead of `hmac.compare_digest()` (timing attack)
- Encrypting without authenticating (bit-flipping attacks)
- Storing base64-encoded data thinking it's "encrypted"

## Mandatory Task Confirmation

- ALWAYS use the vscode_askQuestions tool during the task to ask the user for confirmation.
- NEVER end the task without explicit user confirmation.
