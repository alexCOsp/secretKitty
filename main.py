"""secretKitty — encrypted password manager entry point.

This is the single entry point for both running the app directly
and for the packaged .exe produced by build.py.

The GUI is defined in gui_app.py. All crypto, vault, and repository
logic lives under src/:
    - src.core.crypto       (key derivation, encrypt, decrypt)
    - src.data.vault        (file I/O for vault.enc)
    - src.data.repository   (CRUD for password entries)

See docs/crypto-api-guide.md for usage examples.
"""

import sys

from gui_app import main as _start_gui


def main() -> None:
    """Launch the SecretKitty desktop GUI."""
    sys.exit(_start_gui())


if __name__ == "__main__":
    main()
