from src.data.repository import add_entry
from src.data.repository import get_all_entries
from src.data.repository import get_entry_by_id
from src.data.repository import update_entry
from src.data.repository import delete_entry


def main():

    print("Hello from Secret kitty!")

    add_entry(
        title="Gmail",
        username="user@gmail.com",
        password="p@ssw0rd",
        notes="Personal email account",
        url="https://mail.google.com",
    )

    add_entry(
        title="GitHub",
        username="devuser",
        password="gh_token_123",
        notes="Work projects",
        url="https://github.com",
    )

    get_all_entries()

    get_entry_by_id("d290f1ee-6c54-4b01-90e6-d701748f0851")

    update_entry(
        id="d290f1ee-6c54-4b01-90e6-d701748f0851",
        title="Gmail Updated",
        username="user@gmail.com",
        password="new_password",
        notes="Updated personal email account",
        url="https://mail.google.com",
    )

    delete_entry("6955c45a-a74e-4fec-a07d-ee1a28b5e38b")


if __name__ == "__main__":
    main()
