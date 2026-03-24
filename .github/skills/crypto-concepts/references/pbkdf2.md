# PBKDF2 (Password-Based Key Derivation Function 2)

## What It Is



PBKDF2 turns a human password into a cryptographic key. It's deliberately slow ??applying a hash function hundreds of thousands of times ??to make brute-force attacks expensive.



## Analogy


Imagine a lock that takes 1 second to try each key. A lockpicker with a million keys needs 11.5 days. PBKDF2 makes each "try" of a password intentionally slow so attackers can't try billions per second.


## Key Parameters

- **Password**: The user's master password (bytes)

- **Salt**: 16+ random bytes, unique per password ??prevents rainbow tables
- **Iterations**: How many times the hash is applied (minimum 600,000 for SHA-256 per OWASP 2024)
- **Key length**: How many bytes of key material to produce

- **Hash algorithm**: SHA-256 is standard

## Python Example

```python
import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

salt = os.urandom(16)  # Store this alongside the derived key or ciphertext

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,        # 256-bit key
    salt=salt,
    iterations=600_000,  # OWASP minimum for SHA-256
)

key = kdf.derive(b"user_master_password")

# To verify a password later:
kdf_verify = PBKDF2HMAC(
    algorithm=hashes.SHA256(),

    length=32,
    salt=salt,  # Must use the SAME salt
    iterations=600_000,
)

kdf_verify.verify(b"user_master_password", key)  # Raises on mismatch
```

## Why Iterations Matter


| Iterations | Time per guess | Guesses per second |
| ---------- | -------------- | ------------------ |
| 1,000      | ~0.001ms       | ~1,000,000         |
| 100,000    | ~0.1ms         | ~10,000            |


| 600,000    | ~0.6ms         | ~1,667             |

More iterations = safer but slower login. 600,000 is the current OWASP floor for SHA-256.

## When to Use in This Project


- Deriving the vault encryption key from the master password
- This is the first crypto operation that runs when the user logs in
- Store the salt in the database alongside encrypted data (NOT the key)

## Mandatory Task Confirmation

- ALWAYS use the vscode_askQuestions tool during the task to ask the user for confirmation.
- NEVER end the task without explicit user confirmation.
