import json
from repository import add_entry


def main():
    data = {"entries": []}

    data = add_entry(data, title="Gmail", username="user@gmail.com", password="p@ssw0rd")
    data = add_entry(data, title="GitHub", username="devuser", password="gh_token_123")

    with open("vault.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Save to vault.json")


if __name__ == "__main__":
    main()
