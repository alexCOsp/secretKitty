# secretKitty ??Python Crypto Password Manager

## Project Overview

A desktop password manager built with Python to practice Python programming and applied cryptography. This is a **learning project** ??prioritize clear, educational code over cleverness.

## Tech Stack

- **Language**: Python 3.12+
- **GUI**: tkinter (or PyQt if specified)
- **Crypto**: `cryptography` library (Fernet, PBKDF2, AES-GCM)
- **Storage**: SQLite with encrypted fields
- **Testing**: pytest

## Code Style

- Follow PEP 8 strictly
- Use type hints on all function signatures
- Prefer `pathlib.Path` over `os.path`
- Use `dataclasses` or `pydantic` for data models
- Keep functions under 30 lines

## Architecture

- `src/` ??application source code
- `src/core/` ??crypto primitives, vault logic
- `src/gui/` ??desktop UI components
- `src/models/` ??data models (entries, vaults)
- `tests/` ??mirrors `src/` structure

## Crypto Rules (Critical)

- NEVER implement custom cryptographic algorithms ??use `cryptography` library
- NEVER store passwords in plaintext or log sensitive data
- ALWAYS derive keys with PBKDF2 (minimum 600,000 iterations) or Argon2
- ALWAYS use authenticated encryption (AES-GCM or Fernet)
- ALWAYS use `secrets` module for random generation, never `random`
- ALWAYS zeroize sensitive byte arrays after use when possible
- Salt must be unique per derivation (minimum 16 bytes from `os.urandom`)

## Learning Approach

- When explaining code, include **why** a choice was made, not just what it does
- Reference relevant Python docs or cryptography concepts
- Flag common beginner mistakes and security pitfalls
- Suggest exercises to reinforce concepts when appropriate

## Build & Test

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Mandatory Task Confirmation

- ALWAYS use the vscode_askQuestions tool during the task to ask the user for confirmation.
- NEVER end the task without explicit user confirmation.
