# Crypto API Guide

How to use the crypto and vault modules in secretKitty.

---

## Module Overview

| Module                | Import                                | Responsibility                   |
| --------------------- | ------------------------------------- | -------------------------------- |
| `src.core.crypto`     | `from src.core.crypto import ...`     | Key derivation, encrypt, decrypt |
| `src.data.vault`      | `from src.data.vault import ...`      | Read/write `vault.enc` file      |
| `src.data.repository` | `from src.data.repository import ...` | In-memory CRUD on entries dict   |

**Rule**: The GUI/middleware layer orchestrates these modules. They do NOT call each other (except `vault.py` imports `SALT_LENGTH` from `crypto.py`).

---

## Available Functions

### `src.core.crypto`

#### `generate_salt() -> bytes`

Generate 16 cryptographically random bytes. Call this **once** when creating a new vault.

#### `derive_key(password: str, salt: bytes) -> bytes`

Derive a Fernet-compatible encryption key from the master password and salt.

- Uses PBKDF2-HMAC-SHA256 with 600,000 iterations
- Returns a 44-character URL-safe base64-encoded key
- **Takes ~0.5s** — this is intentional (brute-force protection)

#### `encrypt(key: bytes, plaintext: str) -> bytes`

Encrypt a string (typically JSON) with the Fernet key. Returns an opaque token.

#### `decrypt(key: bytes, token: bytes) -> str`

Decrypt a Fernet token back to the original string. Raises `cryptography.fernet.InvalidToken` if the key is wrong or data is corrupted.

### `src.data.vault`

#### `vault_exists(path?) -> bool`

Check if the vault file exists on disk.

#### `save_vault(salt: bytes, encrypted_data: bytes, path?) -> None`

Write salt + encrypted token to `vault.enc`.

#### `load_vault(path?) -> tuple[bytes, bytes]`

Read `vault.enc` and return `(salt, encrypted_data)`.

### `src.data.repository`

#### `add_entry(data, title, username, password) -> dict`

#### `get_all_entries(data) -> list`

#### `update_entry(data, id, **kwargs) -> dict`

#### `delete_entry(data, id) -> dict`

---

## Flow 1: Create a New Vault (First Run)

```python
import json
from src.core.crypto import generate_salt, derive_key, encrypt
from src.data.vault import save_vault

# 1. Get password from user (use getpass in real code!)
password = "user_master_password"

# 2. Generate a fresh salt (once per vault)
salt = generate_salt()

# 3. Derive encryption key
key = derive_key(password, salt)

# 4. Create empty vault and serialize
data = {"entries": []}
json_str = json.dumps(data, ensure_ascii=False)

# 5. Encrypt and save
token = encrypt(key, json_str)
save_vault(salt, token)
```

## Flow 2: Unlock Existing Vault (Returning User)

```python
import json
from cryptography.fernet import InvalidToken
from src.core.crypto import derive_key, decrypt
from src.data.vault import load_vault

# 1. Get password from user
password = "user_master_password"

# 2. Load salt and encrypted data from file
salt, token = load_vault()

# 3. Re-derive the same key using loaded salt
key = derive_key(password, salt)

# 4. Decrypt — handle wrong password
try:
    json_str = decrypt(key, token)
    data = json.loads(json_str)
except InvalidToken:
    # Wrong password OR corrupted file
    # Show error to user, do NOT reveal which one
    print("Authentication failed")
```

## Flow 3: Save After Changes

```python
import json
from src.core.crypto import encrypt
from src.data.vault import save_vault

# After modifying entries in memory:
json_str = json.dumps(data, ensure_ascii=False)
token = encrypt(key, json_str)
save_vault(salt, token)
# key and salt are the same ones from login — keep them in memory
```

## Flow 4: Add / Read / Update / Delete Entries

```python
from src.data.repository import (
    add_entry,
    get_all_entries,
    update_entry,
    delete_entry,
)

# All operations work on the in-memory dict (NOT disk)
# You must call Flow 3 (save) to persist changes

add_entry(data, title="Gmail", username="me@gmail.com", password="s3cret")

entries = get_all_entries(data)  # sorted by title

update_entry(data, id="some-uuid", password="new_password")

delete_entry(data, id="some-uuid")
```

---

## Security Reminders for GUI/Middleware

| Rule                                                      | Why                                                                |
| --------------------------------------------------------- | ------------------------------------------------------------------ |
| Use `getpass.getpass()` for password input                | Prevents password from showing on screen                           |
| Ask password **twice** on vault creation                  | No recovery if user mistypes — key will be different               |
| Catch `InvalidToken` — don't reveal _why_ it failed       | Prevents attackers from distinguishing wrong-key vs corrupted-data |
| Never log `password`, `key`, `salt`, or `json_str`        | These are sensitive — only in memory                               |
| Call `save_vault()` before app exit                       | Unsaved changes are lost — data is only in memory                  |
| Clear clipboard after copying passwords (e.g., 30s timer) | Prevents password lingering in clipboard                           |
| Consider auto-lock after idle timeout                     | Drop the `key` variable to force re-authentication                
## Security Reminders for GUI/Middleware

| Rule | Why |
|------|-----|
| Use `getpass.getpass()` for password input | Prevents password from showing on screen |
| Ask password **twice** on vault creation | No recovery if user mistypes — key will be different |
| Catch `InvalidToken` — don't reveal *why* it failed | Prevents attackers from distinguishing wrong-key vs corrupted-data |
| Never log `password`, `key`, `salt`, or `json_str` | These are sensitive — only in memory |
| Call `save_vault()` before app exit | Unsaved changes are lost — data is only in memory |
| Clear clipboard after copying passwords (e.g., 30s timer) | Prevents password lingering in clipboard |
| Consider auto-lock after idle timeout | Drop the `key` variable to force re-authentication |

---

## File Format Reference

```
vault.enc:
┌──────────────────┬───────────────────────────┐
│  salt (16 bytes)  │  Fernet token (variable)  │
└──────────────────┴───────────────────────────┘
```

- **Salt**: not secret, stored in clear, unique per vault
- **Fernet token**: contains Version + Timestamp + IV + Ciphertext + HMAC (all base64-encoded)
- **Key**: NEVER stored anywhere — derived from password + salt each time
