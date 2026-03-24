"""Styled PySide6 GUI for browsing and adding password entries."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from repository import add_entry


BASE_DIR = Path(__file__).resolve().parent
VAULT_PATH = BASE_DIR / "vault.json"
CAT_ART_PATH = BASE_DIR / "assets" / "cat.svg"


@dataclass
class VaultState:
    """In-memory state for the simple password vault GUI."""

    entries: list[dict[str, Any]]

    def to_dict(self) -> dict[str, list[dict[str, Any]]]:
        """Return the JSON-serializable vault structure."""
        return {"entries": self.entries}


def load_vault(path: Path) -> VaultState:
    """Load existing vault data or create an empty state."""
    if not path.exists():
        return VaultState(entries=[])

    with path.open("r", encoding="utf-8") as file_obj:
        raw_data = json.load(file_obj)

    entries = raw_data.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("vault.json format is invalid: entries must be a list")

    return VaultState(entries=entries)


def save_vault(path: Path, state: VaultState) -> None:
    """Persist the current vault state to disk."""
    with path.open("w", encoding="utf-8") as file_obj:
        json.dump(state.to_dict(), file_obj, indent=2, ensure_ascii=False)


def build_entry_label(entry: dict[str, Any]) -> str:
    """Format a short label for the entry tree."""
    title = entry.get("title", "Untitled")
    username = entry.get("username", "")
    return f"{title} - {username}" if username else title


class PasswordManagerWindow(QWidget):
    """Desktop application window with sidebar navigation."""

    def __init__(self, vault_path: Path) -> None:
        super().__init__()
        self.vault_path = vault_path
        self.state = load_vault(vault_path)
        self.selected_entry_id: str | None = None

        self.setWindowTitle("SecretKitty Password Manager")
        self.resize(1080, 680)
        self._apply_fonts()

        self.title_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.status_label = QLabel()
        self.detail_label = QLabel()
        self.sidebar_tree = QTreeWidget()

        self._build_layout()
        self._apply_styles()
        self._refresh_sidebar()
        self._set_status(f"Vault file: {self.vault_path.name}")

    def _apply_fonts(self) -> None:
        base_font = QFont("Segoe UI", 10)
        self.setFont(base_font)

    def _build_layout(self) -> None:
        shell_layout = QHBoxLayout()
        shell_layout.setContentsMargins(24, 24, 24, 24)
        shell_layout.setSpacing(18)

        shell_layout.addWidget(self._build_sidebar_card(), 2)
        shell_layout.addWidget(self._build_content_card(), 5)
        self.setLayout(shell_layout)

    def _build_sidebar_card(self) -> QFrame:
        sidebar_card = QFrame()
        sidebar_card.setObjectName("sidebarCard")

        title_label = QLabel("Navigator")
        title_label.setObjectName("sectionTitle")
        subtitle_label = QLabel("Browse items in a tree view.")
        subtitle_label.setObjectName("sectionSubtitle")

        self.sidebar_tree.setHeaderHidden(True)
        self.sidebar_tree.itemSelectionChanged.connect(self._handle_tree_selection)

        layout = QVBoxLayout()
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addWidget(self.sidebar_tree)
        sidebar_card.setLayout(layout)
        return sidebar_card

    def _build_content_card(self) -> QFrame:
        content_card = QFrame()
        content_card.setObjectName("contentCard")

        layout = QVBoxLayout()
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)
        layout.addLayout(self._build_hero_row())
        layout.addWidget(self._build_form_card())
        layout.addWidget(self.status_label)
        content_card.setLayout(layout)
        return content_card

    def _build_hero_row(self) -> QHBoxLayout:
        hero_row = QHBoxLayout()
        hero_row.setSpacing(18)

        text_card = QFrame()
        text_card.setObjectName("heroTextCard")
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("SecretKitty Vault")
        title_label.setObjectName("heroTitle")
        subtitle_label = QLabel(
            "A gentle desktop shell for adding and browsing your account entries."
        )
        subtitle_label.setWordWrap(True)
        subtitle_label.setObjectName("heroSubtitle")

        self.detail_label.setObjectName("detailLabel")
        self.detail_label.setWordWrap(True)

        text_layout.addWidget(title_label)
        text_layout.addWidget(subtitle_label)
        text_layout.addWidget(self.detail_label)
        text_layout.addStretch()
        text_card.setLayout(text_layout)

        art_card = QFrame()
        art_card.setObjectName("artCard")
        art_layout = QVBoxLayout()
        art_layout.setContentsMargins(12, 12, 12, 12)
        art_layout.addWidget(
            QSvgWidget(str(CAT_ART_PATH)),
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        art_card.setLayout(art_layout)

        hero_row.addWidget(text_card, 3)
        hero_row.addWidget(art_card, 2)
        return hero_row

    def _build_form_card(self) -> QFrame:
        form_card = QFrame()
        form_card.setObjectName("formCard")

        form_layout = QFormLayout()
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(14)
        form_layout.addRow("Title", self.title_input)
        form_layout.addRow("Username", self.username_input)
        form_layout.addRow("Password", self.password_input)

        save_button = QPushButton("Add entry")
        save_button.clicked.connect(self._handle_add_entry)

        clear_button = QPushButton("Clear form")
        clear_button.setObjectName("secondaryButton")
        clear_button.clicked.connect(self._clear_form)

        button_row = QHBoxLayout()
        button_row.addWidget(save_button)
        button_row.addWidget(clear_button)
        button_row.addStretch()

        wrapper_layout = QVBoxLayout()
        wrapper_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("Entry editor")
        title_label.setObjectName("sectionTitle")
        subtitle_label = QLabel(
            "Select an item on the left to inspect it, or create a new one here."
        )
        subtitle_label.setObjectName("sectionSubtitle")

        wrapper_layout.addWidget(title_label)
        wrapper_layout.addWidget(subtitle_label)
        wrapper_layout.addLayout(form_layout)
        wrapper_layout.addLayout(button_row)
        form_card.setLayout(wrapper_layout)
        return form_card

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background: #f7efe3;
                color: #46352a;
            }
            QFrame#sidebarCard,
            QFrame#contentCard,
            QFrame#heroTextCard,
            QFrame#artCard,
            QFrame#formCard {
                background: #fffaf3;
                border: 1px solid #ead8c6;
                border-radius: 22px;
            }
            QFrame#heroTextCard {
                background: #fff4df;
            }
            QFrame#artCard {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #f9d9ad,
                    stop: 1 #f4b183
                );
            }
            QLabel#heroTitle {
                font-size: 30px;
                font-weight: 700;
                color: #7c4a2d;
            }
            QLabel#heroSubtitle,
            QLabel#sectionSubtitle,
            QLabel#detailLabel,
            QLabel {
                color: #6f5849;
            }
            QLabel#sectionTitle {
                font-size: 18px;
                font-weight: 700;
                color: #5c3b2a;
            }
            QLineEdit {
                min-height: 40px;
                padding: 8px 12px;
                border-radius: 12px;
                border: 1px solid #dec5b0;
                background: #fffdf9;
                selection-background-color: #cf8f62;
            }
            QLineEdit:focus {
                border: 2px solid #cf8f62;
            }
            QPushButton {
                min-height: 42px;
                padding: 0 18px;
                border: none;
                border-radius: 14px;
                background: #c97c4f;
                color: white;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #b86e45;
            }
            QPushButton#secondaryButton {
                background: #ead8c6;
                color: #6d4b39;
            }
            QPushButton#secondaryButton:hover {
                background: #e2ccb7;
            }
            QTreeWidget {
                background: #fffdf9;
                border: 1px solid #ead8c6;
                border-radius: 16px;
                padding: 8px;
            }
            QTreeWidget::item {
                min-height: 34px;
                border-radius: 10px;
                padding: 4px 8px;
            }
            QTreeWidget::item:selected {
                background: #f4c9a8;
                color: #523325;
            }
            """
        )

    def _handle_add_entry(self) -> None:
        title = self.title_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not title or not username or not password:
            QMessageBox.warning(self, "Missing fields", "Please fill all fields.")
            return

        data = self.state.to_dict()
        updated_data = add_entry(data, title=title, username=username, password=password)
        self.state = VaultState(entries=updated_data["entries"])
        save_vault(self.vault_path, self.state)
        self._refresh_sidebar()
        self._clear_form()
        self._set_status(f"Saved '{title}' to {self.vault_path.name}")

    def _handle_tree_selection(self) -> None:
        item = self.sidebar_tree.currentItem()
        if item is None:
            return

        entry_id = item.data(0, Qt.ItemDataRole.UserRole)
        if entry_id is None:
            self.selected_entry_id = None
            self.detail_label.setText(
                f"{len(self.state.entries)} entries available in your local vault."
            )
            return

        entry = self._find_entry_by_id(str(entry_id))
        if entry is None:
            return

        self.selected_entry_id = str(entry_id)
        self.title_input.setText(entry.get("title", ""))
        self.username_input.setText(entry.get("username", ""))
        self.password_input.setText(entry.get("password", ""))
        created_at = entry.get("created_at", "")
        self.detail_label.setText(
            f"Selected: {entry.get('title', 'Untitled')}\n"
            f"Username: {entry.get('username', '')}\n"
            f"Created: {created_at}"
        )

    def _refresh_sidebar(self) -> None:
        self.sidebar_tree.clear()
        root_item = QTreeWidgetItem(["All Entries"])
        root_item.setData(0, Qt.ItemDataRole.UserRole, None)
        self.sidebar_tree.addTopLevelItem(root_item)

        for entry in self.state.entries:
            item = QTreeWidgetItem([build_entry_label(entry)])
            item.setData(0, Qt.ItemDataRole.UserRole, entry.get("id"))
            root_item.addChild(item)

        root_item.setExpanded(True)
        self.sidebar_tree.setCurrentItem(root_item)
        self.detail_label.setText(
            f"{len(self.state.entries)} entries available in your local vault."
        )

    def _find_entry_by_id(self, entry_id: str) -> dict[str, Any] | None:
        for entry in self.state.entries:
            if entry.get("id") == entry_id:
                return entry
        return None

    def _clear_form(self) -> None:
        self.title_input.clear()
        self.username_input.clear()
        self.password_input.clear()
        self.title_input.setFocus()

    def _set_status(self, message: str) -> None:
        self.status_label.setText(message)


def main() -> int:
    """Start the standalone PySide6 desktop application."""
    app = QApplication(sys.argv)
    window = PasswordManagerWindow(VAULT_PATH)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())