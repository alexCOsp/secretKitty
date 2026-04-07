import uuid
import json
from datetime import datetime


# ── READ JSON FILE ──────────────────────────────
def read_json_file() -> dict:
    with open("vault.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


# ── WRITE JSON FILE ──────────────────────────────
def write_json_file(data: dict) -> None:
    with open("vault.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ── UPDATE ──────────────────────────────
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
    currentData = read_json_file()

    # Add new entry
    currentData["entries"].append(newEntry)

    # Write updated data back to file
    write_json_file(currentData)

    print("Save to vault.json")


# ── READ（All）────────────────────────
def get_all_entries() -> list:

    data = read_json_file()

    print(sorted(data["entries"], key=lambda e: e["title"]))
    return sorted(data["entries"], key=lambda e: e["title"])


# ── READ（SINGLE）────────────────────────
def get_entry_by_id(id: str) -> dict | None:
    data = read_json_file()

    for entry in data["entries"]:
        if entry["id"] == id:
            print(entry)
            return entry
    print(f"Entry with id {id} not found.")
    return None


# ── UPDATE ──────────────────────────────
def update_entry(
    id: str, title: str, username: str, password: str, notes: str, url: str
) -> dict:
    data = read_json_file()
    for entry in data["entries"]:
        if entry["id"] == id:
            entry.update(
                {
                    "title": title,
                    "username": username,
                    "password": password,
                    "notes": notes,
                    "url": url,
                    "updated_at": datetime.now().isoformat(),
                }
            )
            print(f"Entry with id {id} updated.")
            write_json_file(data)
            break
        else:
            print(f"Entry with id {id} not found.")
    return data


# ── DELETE ──────────────────────────────
def delete_entry(id: str) -> dict:
    data = read_json_file()
    for entry in data["entries"]:
        if entry["id"] == id:
            data["entries"].remove(entry)
            print(f"Entry with id {id} deleted.")
            break
        else:
            print(f"Entry with id {id} not found.")
    write_json_file(data)
    return data
