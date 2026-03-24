# AES-GCM (Galois/Counter Mode)

## What It Is

AES-GCM combines AES encryption with a built-in authentication tag. It encrypts your data AND proves it hasn't been tampered with ??in one operation.

## Analogy

Think of a sealed, tamper-evident envelope. AES encrypts (seals the letter), and GCM adds the tamper-evident strip. If anyone changes even one bit, the recipient knows.

## Key Parameters

- **Key**: 128 or 256 bits (use 256 for this project)
- **Nonce/IV**: 12 bytes, MUST be unique per encryption with the same key
- **Plaintext**: The data to encrypt
- **Associated Data** (optional): Data authenticated but not encrypted (e.g., metadata)

## Python Example

```python
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Generate a 256-bit key (in practice, derive from password via PBKDF2)
key = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(key)

# Encrypt ??nonce MUST be unique every time
nonce = os.urandom(12)
ciphertext = aesgcm.encrypt(nonce, b"my secret data", None)

# Decrypt
plaintext = aesgcm.decrypt(nonce, ciphertext, None)
```

## Why Nonce Uniqueness Matters

Reusing a nonce with the same key in GCM is catastrophic ??it lets an attacker recover the authentication key and forge messages. Always generate a fresh random nonce.

## When to Use in This Project

- Encrypting individual vault entries where you need fine control
- When you need associated data (e.g., authenticating the entry title without encrypting it)
- When Fernet's overhead or format is too restrictive

## Mandatory Task Confirmation

- ALWAYS use the vscode_askQuestions tool during the task to ask the user for confirmation.
- NEVER end the task without explicit user confirmation.
