from repository import add_entry
from repository import get_all_entries


def main():

    print("Hello from Secret kitty!")

    data = {"entries": []}

    add_entry(data, title="Gmail", username="user@gmail.com", password="p@ssw0rd", notes="Personal email account", url="https://mail.google.com")

    add_entry(data, title="GitHub", username="devuser", password="gh_token_123", notes="Work projects", url="https://github.com")

    get_all_entries(data)


if __name__ == "__main__":
    main()
