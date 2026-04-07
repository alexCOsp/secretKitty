import uuid
import json
from datetime import datetime


# ── CREATE ──────────────────────────────
def add_entry(title: str, username: str, password: str, notes: str, url: str) -> None:

    newEntry = {
        "id": str(uuid.uuid4()),
        "title": title,
        "username": username,
        "password": password,  # encrypted by crypto.py
        "notes": notes,
        "url": url,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    # Read existing data
    with open("vault.json", "r", encoding="utf-8") as f:
        currentData: dict[str, list] = json.load(f)

    # Add new entry
    currentData["entries"].append(newEntry)

    # Write updated data back to file
    with open("vault.json", "w", encoding="utf-8") as f:
        json.dump(currentData, f, indent=2, ensure_ascii=False)

    print("Save to vault.json")


# ── READ（All）────────────────────────
def get_all_entries() -> list:

    with open("vault.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    print(sorted(data["entries"], key=lambda e: e["title"]))
    return sorted(data["entries"], key=lambda e: e["title"])


# ── READ（SINGLE）────────────────────────
def get_entry_by_id(id: str) -> dict | None:
    with open("vault.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for entry in data["entries"]:
        if entry["id"] == id:
            print(entry)
            return entry
    print(f"Entry with id {id} not found.")
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
