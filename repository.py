import uuid
import json
from datetime import datetime


# ── CREATE ──────────────────────────────
def add_entry(data: dict, title, username, password, notes: str, url: str):
    entry = {
        "id": str(uuid.uuid4()),
        "title": title,
        "username": username,
        "password": password,  # encrypted by crypto.py
        "notes": notes,
        "url": url,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    data["entries"].append(entry)

    with open("vault.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Save to vault.json")


# ── READ（All）────────────────────────
def get_all_entries(data: dict) -> list:
    print(sorted(data["entries"], key=lambda e: e["title"]))
    return sorted(data["entries"], key=lambda e: e["title"])


# ── READ（SINGLE）────────────────────────
def get_entry_by_id(data: dict, id: str) -> dict | None:
    for entry in data["entries"]:
        if entry["id"] == id:
            print(entry)
            return entry
        else:
            print(f"Entry with id {id} not found.")
            return None
    return None


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
