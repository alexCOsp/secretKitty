import json
from pathlib import Path
from unittest.mock import patch

from src.core.crypto import derive_key, encrypt, generate_salt
from src.data.repository import (
    read_json_file,
    write_json_file,
    add_entry,
    get_all_entries,
    get_entry_by_id,
    update_entry,
    delete_entry,
)
from src.data.vault import VAULT_PATH, save_vault

PASSWORD = "test-password-123"

SAMPLE: dict = {
    "entries": [
        {
            "id": "id-alpha",
            "title": "Alpha",
            "username": "alice",
            "password": "pw-alpha",
            "notes": "note-alpha",
            "url": "https://alpha.example.com",
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-01T00:00:00",
        },
        {
            "id": "id-beta",
            "title": "Beta",
            "username": "bob",
            "password": "pw-beta",
            "notes": "note-beta",
            "url": "https://beta.example.com",
            "created_at": "2026-01-02T00:00:00",
            "updated_at": "2026-01-02T00:00:00",
        },
    ]
}


def seed_vault() -> None:
    salt = generate_salt()
    key = derive_key(PASSWORD, salt)
    token = encrypt(key, json.dumps(SAMPLE, ensure_ascii=False))
    save_vault(salt, token)


def cleanup() -> None:
    p = Path(VAULT_PATH)
    if p.exists():
        p.unlink()


def test_read_json_file() -> None:
    with patch("src.data.repository.getpass", return_value=PASSWORD):
        data = read_json_file()
    assert data["entries"][0]["title"] == "Alpha"
    print("[OK] read_json_file")


def test_write_json_file() -> None:
    new_data = {
        "entries": [
            {
                "id": "id-written",
                "title": "Written",
                "username": "w",
                "password": "w",
                "notes": "",
                "url": "",
                "created_at": "2026-02-01T00:00:00",
                "updated_at": "2026-02-01T00:00:00",
            }
        ]
    }
    with patch("src.data.repository.getpass", return_value=PASSWORD):
        write_json_file(new_data)
        data = read_json_file()
    assert len(data["entries"]) == 1
    assert data["entries"][0]["title"] == "Written"
    print("[OK] write_json_file")


def test_add_entry() -> None:
    with patch("src.data.repository.getpass", return_value=PASSWORD):
        add_entry("Gamma", "carol", "pw-gamma", "note-gamma", "https://gamma.example.com")
        data = read_json_file()
    titles = [e["title"] for e in data["entries"]]
    assert "Gamma" in titles
    print("[OK] add_entry")


def test_get_all_entries() -> None:
    with patch("src.data.repository.getpass", return_value=PASSWORD):
        entries = get_all_entries()
    titles = [e["title"] for e in entries]
    assert titles == sorted(titles)
    print("[OK] get_all_entries")


def test_get_entry_by_id() -> None:
    with patch("src.data.repository.getpass", return_value=PASSWORD):
        entry = get_entry_by_id("id-alpha")
    assert entry is not None
    assert entry["title"] == "Alpha"

    with patch("src.data.repository.getpass", return_value=PASSWORD):
        missing = get_entry_by_id("id-does-not-exist")
    assert missing is None
    print("[OK] get_entry_by_id")


def test_update_entry() -> None:
    with patch("src.data.repository.getpass", return_value=PASSWORD):
        update_entry(
            "id-alpha",
            "Alpha Updated",
            "alice2",
            "pw-alpha2",
            "note-alpha2",
            "https://alpha2.example.com",
        )
        entry = get_entry_by_id("id-alpha")
    assert entry is not None
    assert entry["title"] == "Alpha Updated"
    assert entry["username"] == "alice2"
    print("[OK] update_entry")


def test_delete_entry() -> None:
    with patch("src.data.repository.getpass", return_value=PASSWORD):
        delete_entry("id-beta")
        entry = get_entry_by_id("id-beta")
    assert entry is None
    print("[OK] delete_entry")


def run() -> None:
    tests = [
        test_read_json_file,
        test_write_json_file,
        test_add_entry,
        test_get_all_entries,
        test_get_entry_by_id,
        test_update_entry,
        test_delete_entry,
    ]
    for t in tests:
        cleanup()
        seed_vault()
        try:
            t()
        except Exception as e:
            print(f"[FAIL] {t.__name__}: {e}")
            raise
    cleanup()
    print("All repository tests passed.")


if __name__ == "__main__":
    run()
