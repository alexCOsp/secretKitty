# 加密 API 使用指南

secretKitty 密碼管理器的加密與保險庫模組使用方式。

---

## 模組總覽

| 模組                  | 匯入方式                              | 職責                  |
| --------------------- | ------------------------------------- | --------------------- |
| `src.core.crypto`     | `from src.core.crypto import ...`     | 金鑰衍生、加密、解密  |
| `src.data.vault`      | `from src.data.vault import ...`      | 讀寫 `vault.enc` 檔案 |
| `src.data.repository` | `from src.data.repository import ...` | 記憶體中的 CRUD 操作  |

**原則**：GUI / 中介層負責串接這些模組。它們彼此不互相呼叫（`vault.py` 僅匯入 `crypto.py` 的 `SALT_LENGTH` 常數）。

---

## 可用函式

### `src.core.crypto`

#### `generate_salt() -> bytes`

產生 16 位元組的加密安全隨機鹽值。建立新保險庫時呼叫**一次**。

#### `derive_key(password: str, salt: bytes) -> bytes`

從主密碼和鹽值衍生 Fernet 相容的加密金鑰。

- 使用 PBKDF2-HMAC-SHA256，600,000 次迭代
- 回傳 44 字元的 URL-safe base64 編碼金鑰
- **約需 0.5 秒**——這是刻意的（暴力破解防護）

#### `encrypt(key: bytes, plaintext: str) -> bytes`

使用 Fernet 金鑰加密字串（通常是 JSON）。回傳不透明的 token。

#### `decrypt(key: bytes, token: bytes) -> str`

將 Fernet token 解密回原始字串。若金鑰錯誤或資料被竄改，會拋出 `cryptography.fernet.InvalidToken`。

### `src.data.vault`

#### `vault_exists(path?) -> bool`

檢查保險庫檔案是否存在。

#### `save_vault(salt: bytes, encrypted_data: bytes, path?) -> None`

將鹽值 + 加密 token 寫入 `vault.enc`。

#### `load_vault(path?) -> tuple[bytes, bytes]`

讀取 `vault.enc` 並回傳 `(salt, encrypted_data)`。

### `src.data.repository`

#### `add_entry(data, title, username, password) -> dict`

#### `get_all_entries(data) -> list`

#### `update_entry(data, id, **kwargs) -> dict`

#### `delete_entry(data, id) -> dict`

---

## 流程 1：建立新保險庫（首次使用）

```python
import json
from src.core.crypto import generate_salt, derive_key, encrypt
from src.data.vault import save_vault

# 1. 從使用者取得密碼（正式程式請用 getpass！）
password = "user_master_password"

# 2. 產生新的鹽值（每個保險庫一次）
salt = generate_salt()

# 3. 衍生加密金鑰
key = derive_key(password, salt)

# 4. 建立空保險庫並序列化
data = {"entries": []}
json_str = json.dumps(data, ensure_ascii=False)

# 5. 加密並儲存
token = encrypt(key, json_str)
save_vault(salt, token)
```

## 流程 2：解鎖現有保險庫（回頭使用者）

```python
import json
from cryptography.fernet import InvalidToken
from src.core.crypto import derive_key, decrypt
from src.data.vault import load_vault

# 1. 從使用者取得密碼
password = "user_master_password"

# 2. 從檔案載入鹽值和加密資料
salt, token = load_vault()

# 3. 用載入的鹽值重新衍生同一把金鑰
key = derive_key(password, salt)

# 4. 解密——處理密碼錯誤的情況
try:
    json_str = decrypt(key, token)
    data = json.loads(json_str)
except InvalidToken:
    # 密碼錯誤或檔案損壞
    # 顯示錯誤訊息，不要透露是哪一種
    print("驗證失敗")
```

## 流程 3：修改後儲存

```python
import json
from src.core.crypto import encrypt
from src.data.vault import save_vault

# 在記憶體中修改 entries 之後：
json_str = json.dumps(data, ensure_ascii=False)
token = encrypt(key, json_str)
save_vault(salt, token)
# key 和 salt 是登入時取得的——保留在記憶體中
```

## 流程 4：新增 / 讀取 / 更新 / 刪除條目

```python
from src.data.repository import (
    add_entry,
    get_all_entries,
    update_entry,
    delete_entry,
)

# 所有操作都在記憶體中的 dict 上執行（不碰磁碟）
# 必須呼叫流程 3（儲存）才會寫入磁碟

add_entry(data, title="Gmail", username="me@gmail.com", password="s3cret")

entries = get_all_entries(data)  # 依標題排序

update_entry(data, id="some-uuid", password="new_password")

delete_entry(data, id="some-uuid")
```

---

## GUI / 中介層安全提醒

| 規則                                             | 原因                                     |
| ------------------------------------------------ | ---------------------------------------- |
| 使用 `getpass.getpass()` 輸入密碼                | 防止密碼顯示在螢幕上                     |
| 建立保險庫時密碼輸入**兩次**                     | 打錯密碼就無法復原——金鑰會不同           |
| 捕捉 `InvalidToken`——不要透露*失敗原因*          | 防止攻擊者區分「金鑰錯誤」和「資料損壞」 |
| 絕不記錄 `password`、`key`、`salt` 或 `json_str` | 這些是敏感資料——只存在記憶體             |
| 離開前呼叫 `save_vault()`                        | 未儲存的變更會遺失——資料只在記憶體中     |
| 複製密碼後清除剪貼簿（如 30 秒計時器）           | 防止密碼殘留在剪貼簿                     |
| 考慮閒置逾時自動鎖定                             | 丟棄 `key` 變數以強制重新驗證            |

---

## 檔案格式參考

```
vault.enc:
┌──────────────────┬───────────────────────────┐
│  salt (16 bytes)  │  Fernet token (可變長度)   │
└──────────────────┴───────────────────────────┘
```

- **鹽值 (Salt)**：非機密，明文儲存，每個保險庫唯一
- **Fernet token**：包含 Version + Timestamp + IV + Ciphertext + HMAC（全部 base64 編碼）
- **金鑰 (Key)**：**絕不儲存**——每次從密碼 + 鹽值即時衍生
