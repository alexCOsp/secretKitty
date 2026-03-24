# Hashing vs Encryption

## The Core Difference

- **Encryption** is reversible: plaintext ??ciphertext ??plaintext (with the key)
- **Hashing** is one-way: input ??fixed-size digest (no way back)

## Analogy

- **Encryption** = locking a box with a key. You can always unlock it if you have the key.
- **Hashing** = putting something through a meat grinder. You can verify "was this the same steak?" by grinding another and comparing, but you can't un-grind it.

## When to Use Each

| Scenario                      | Use                      | Why                                               |
| ----------------------------- | ------------------------ | ------------------------------------------------- |
| Store master password proof   | Hash (via PBKDF2/Argon2) | You never need the password back ??just verify it |
| Store vault entries           | Encrypt (AES-GCM/Fernet) | You need to read the passwords back               |
| Generate password fingerprint | Hash                     | Quick comparison without revealing content        |
| Transmit sensitive data       | Encrypt                  | Recipient needs to read it                        |

## Common Mistake

Using `hashlib.sha256(password)` directly for password storage. Problems:

1. **No salt** ??identical passwords produce identical hashes (rainbow tables)
2. **Too fast** ??SHA-256 does billions per second on a GPU
3. **No key stretching** ??no iteration count to slow attackers

Always use PBKDF2 or Argon2 for password hashing ??they add salt and iterations.

## In This Project

- **Hash** the master password (via PBKDF2/Argon2) to verify login
- **Derive a key** from the master password (via PBKDF2/Argon2) to encrypt the vault
- **Encrypt** stored passwords, usernames, and notes so they can be retrieved

## Mandatory Task Confirmation

- ALWAYS use the vscode_askQuestions tool during the task to ask the user for confirmation.
- NEVER end the task without explicit user confirmation.
