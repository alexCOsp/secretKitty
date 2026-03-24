# Argon2 (Memory-Hard Key Derivation)

## What It Is

Argon2 is a modern password hashing function that won the 2015 Password Hashing Competition. Unlike PBKDF2 which is only CPU-hard, Argon2 is also memory-hard ??attackers need large amounts of RAM per guess, making GPU/ASIC attacks impractical.

## Analogy

PBKDF2 forces attackers to do lots of math (CPU work). Argon2 also forces them to rent a lot of desk space (memory). GPUs have tons of math power but limited desk space per core ??so Argon2 neutralizes their advantage.

## Variants

- **Argon2id**: Recommended ??hybrid of Argon2i and Argon2d, resists both side-channel and GPU attacks
- **Argon2i**: Optimized for side-channel resistance (less common)
- **Argon2d**: Optimized for GPU resistance (less common)

## Python Example

```python
from argon2 import PasswordHasher

ph = PasswordHasher(
    time_cost=3,        # Number of iterations
    memory_cost=65536,  # 64 MB of memory
    parallelism=4,      # Threads
)

# Hash a password (salt generated automatically)
hashed = ph.hash("user_master_password")

# Verify
try:
    ph.verify(hashed, "user_master_password")
except argon2.exceptions.VerifyMismatchError:
    print("Wrong password")

# Check if rehash needed (params changed)
if ph.check_needs_rehash(hashed):
    new_hash = ph.hash("user_master_password")
```

## PBKDF2 vs Argon2

| Feature        | PBKDF2         | Argon2id      |
| -------------- | -------------- | ------------- |
| CPU-hard       | Yes            | Yes           |
| Memory-hard    | No             | Yes           |
| GPU-resistant  | Weak           | Strong        |
| Stdlib support | `cryptography` | `argon2-cffi` |
| Maturity       | 20+ years      | ~10 years     |

## When to Use in This Project

- Preferred over PBKDF2 if you want stronger protection
- Requires the `argon2-cffi` package: `pip install argon2-cffi`
- Good upgrade path: start with PBKDF2 to learn, migrate to Argon2 later

## Mandatory Task Confirmation

- ALWAYS use the vscode_askQuestions tool during the task to ask the user for confirmation.
- NEVER end the task without explicit user confirmation.
