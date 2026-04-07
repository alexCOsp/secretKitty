"""secretKitty — encrypted password manager entry point.

The GUI/middleware layer should import from:
    - src.core.crypto   (key derivation, encrypt, decrypt)
    - src.data.vault    (file I/O for vault.enc)
    - src.data.repository (in-memory CRUD for entries)

See docs/crypto-api-guide.md for usage examples.
"""


def main() -> None:
    print("🐱 secretKitty Password Manager")
    print("   Crypto core ready. Waiting for GUI integration.")


if __name__ == "__main__":
    main()
