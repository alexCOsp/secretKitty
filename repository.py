import uuid
from datetime import datetime


# ── CREATE ──────────────────────────────
def add_entry(
    data: dict,
    title: str,
    username: str,
    password: str,
) -> dict:
    """Add a new entry to the in-memory vault data and return it."""
    entry = {
        "id": str(uuid.uuid4()),
        "title": title,
        "username": username,
        "password": password,  # encrypted by crypto.py
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    data["entries"].append(entry)
    return data


# ── READ（All）────────────────────────
def get_all_entries(data: dict) -> list:
    return sorted(data["entries"], key=lambda e: e["title"])


# ── UPDATE ──────────────────────────────
def update_entry(data: dict, id: str, **kwargs) -> dict:
    for entry in data["entries"]:
        if entry["id"] == id:
            entry.update(kwargs)
            entry["updated_at"] = datetime.now().isoformat()
            break
    return data


def delete_entry(data: dict, id: str) -> dict:
    data["entries"] = [e for e in data["entries"] if e["id"] != id]
    return data
