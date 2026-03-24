# Salts, Nonces, and IVs

## Overview

All three are random values mixed into crypto operations. They serve different purposes but share one rule: **don't reuse them improperly.**

| Term  | Full Name             | Used In                         | Must Be Unique Per...    |
| ----- | --------------------- | ------------------------------- | ------------------------ |
| Salt  | Salt                  | Key derivation (PBKDF2, Argon2) | Password                 |
| Nonce | Number used once      | AEAD encryption (AES-GCM)       | Encryption with same key |
| IV    | Initialization Vector | Block cipher modes (CBC)        | Encryption with same key |

## Salt

**Purpose**: Ensures identical passwords produce different derived keys.

Without salt: `hash("password123")` always ??same output. Attacker precomputes a table of common passwords ??instant lookup (rainbow table).

With salt: `hash("password123" + random_salt)` ??unique output every time. Attacker must brute-force each password individually.

```python
import os
salt = os.urandom(16)  # 16 bytes minimum
# Store the salt alongside the hash ??it's not secret, just unique
```

## Nonce

**Purpose**: Ensures encrypting the same plaintext twice with the same key produces different ciphertext.

In AES-GCM, reusing a nonce with the same key is **catastrophic** ??it leaks the authentication key and allows message forgery.

```python
import os
nonce = os.urandom(12)  # 12 bytes for AES-GCM
# Store alongside ciphertext ??not secret, but MUST be unique per encryption
```

## IV (Initialization Vector)

**Purpose**: Same as nonce, but the term is used with CBC mode. Fernet handles IVs automatically.

## Key Rules

1. **Salts/nonces are NOT secret** ??store them alongside encrypted data
2. **Salts/nonces MUST be unique** ??generate randomly each time
3. **Never derive salts from the password itself** ??defeats the purpose
4. **Use `os.urandom()`** ??never `random.randint()` or timestamps

## In This Project

- **Salt**: Generated when creating a vault, stored in the database header
- **Nonce/IV**: Generated per encryption operation, stored with each ciphertext
- Fernet handles IVs internally ??you only manage salts for key derivation

## Mandatory Task Confirmation

- ALWAYS use the vscode_askQuestions tool during the task to ask the user for confirmation.
- NEVER end the task without explicit user confirmation.
