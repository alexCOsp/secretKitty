from repository import add_entry
from repository import get_all_entries
from repository import get_entry_by_id


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


if __name__ == "__main__":
    main()
