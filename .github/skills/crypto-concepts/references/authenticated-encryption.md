# Authenticated Encryption

## The Problem

Basic encryption (AES-CBC, AES-CTR) hides data but doesn't detect tampering. An attacker can flip bits in ciphertext, and decryption produces corrupted plaintext without warning.

## Analogy

Regular encryption = writing in a secret code. Authenticated encryption = writing in a secret code inside a tamper-evident envelope. If someone changes the message, the envelope shows it was opened.

## Bit-Flipping Attack Example

With unauthenticated AES-CTR:

```
Original plaintext:  "transfer $100"
Attacker flips bits in ciphertext...
Decrypted result:    "transfer $900"
```

No error raised ??the application trusts the corrupted data.

## Solution: Authenticated Encryption

Authenticated encryption adds a **tag** (MAC) computed over the ciphertext. Before decrypting, verify the tag. If the ciphertext was modified, verification fails.

Two approaches:

1. **AEAD (recommended)**: AES-GCM does encryption + authentication in one step
2. **Encrypt-then-MAC**: Encrypt with AES-CBC, then HMAC the ciphertext (what Fernet does)

## Python Example (AES-GCM)

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

key = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(key)
nonce = os.urandom(12)

# Encrypt with authentication
ciphertext = aesgcm.encrypt(nonce, b"secret data", b"associated metadata")

# Tamper with ciphertext
tampered = bytearray(ciphertext)
tampered[0] ^= 0xFF

# Decrypt tampered data ??raises InvalidTag
try:
    aesgcm.decrypt(nonce, bytes(tampered), b"associated metadata")
except Exception as e:
    print(f"Tampering detected: {e}")
```

## In This Project

- **Always** use authenticated encryption (AES-GCM or Fernet)
- **Never** use raw AES-CBC or AES-CTR without a MAC
- If someone gains access to your database file but not your key, they can't silently corrupt entries ??decryption will fail with an authentication error

## Mandatory Task Confirmation

- ALWAYS use the vscode_askQuestions tool during the task to ask the user for confirmation.
- NEVER end the task without explicit user confirmation.
