from repository import add_entry


def main():

    print("Hello from Secret kitty!")

    data = {"entries": []}

    add_entry(data, title="Gmail", username="user@gmail.com", password="p@ssw0rd")

    add_entry(data, title="GitHub", username="devuser", password="gh_token_123")


if __name__ == "__main__":
    main()
