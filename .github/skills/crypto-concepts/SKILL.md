---
name: crypto-concepts
description: "Explain cryptographic concepts used in the password manager: symmetric encryption, AES-GCM, Fernet, key derivation (PBKDF2, Argon2), hashing, salting, authenticated encryption, nonces, timing attacks, and when/why to use each."
---

# Crypto Concepts Reference

## When to Use

- User asks "what is..." or "how does... work" about a crypto topic
- User needs to choose between crypto algorithms or approaches
- User is confused about why a particular crypto practice matters
- Before implementing any crypto feature, to explain the underlying concept

## Procedure

1. Identify which concept the user is asking about
2. Load the relevant reference file below
3. Explain at the appropriate level ??start simple, add depth if asked

## Concept References

### Symmetric Encryption

- [AES-GCM explained](./references/aes-gcm.md)
- [Fernet (high-level encryption)](./references/fernet.md)

### Key Derivation

- [PBKDF2 and why iterations matter](./references/pbkdf2.md)
- [Argon2 and memory-hard functions](./references/argon2.md)

### Fundamentals

- [Hashing vs Encryption](./references/hashing-vs-encryption.md)
- [Salts, nonces, and IVs](./references/salts-nonces-ivs.md)
- [Authenticated encryption and why it matters](./references/authenticated-encryption.md)

## Teaching Approach

- Start with an analogy or real-world comparison
- Show a minimal Python code example using the `cryptography` library
- Explain what would go wrong if the concept is ignored (the attack)
- Connect back to where this concept appears in the password manager

## Mandatory Task Confirmation

- ALWAYS use the vscode_askQuestions tool during the task to ask the user for confirmation.
- NEVER end the task without explicit user confirmation.
