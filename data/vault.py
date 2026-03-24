import json
import os
from pathlib import Path

VAULT_PATH = "vault.enc"


# ── If file exists ─────────────────────────
def vault_exists() -> bool:
    return Path(VAULT_PATH).exists()

