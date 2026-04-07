"""Styled PySide6 GUI for browsing and adding password entries."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PySide6.QtCore import QEvent, QPointF, QTimer, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

MODULE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = MODULE_DIR.parent.parent
VAULT_PATH = PROJECT_ROOT / "vault.json"
LOGIN_PASSWORD = "1234"

from src.data.repository import add_entry, delete_entry, update_entry


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


class GuardianCatWidget(QWidget):
    """Draw a cyber cat whose pupils track the current cursor position."""

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumSize(220, 220)
        self._anger_level = 0
        self._cursor_timer = QTimer(self)
        self._cursor_timer.timeout.connect(self.update)
        self._cursor_timer.start(33)

    def set_anger_level(self, anger_level: int) -> None:
        """Update the cat mood for login feedback."""
        self._anger_level = max(0, min(anger_level, 4))
        self.update()

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(10, 10, -10, -10)
        center = QPointF(rect.center())

        painter.fillRect(self.rect(), QColor("#0b2030"))
        self._draw_background_glow(painter, center)
        self._draw_data_lines(painter, center)
        self._draw_cat_body(painter, center)
        self._draw_cat_head(painter, center)

    def _draw_cat_body(self, painter: QPainter, center: QPointF) -> None:
        painter.setPen(QPen(QColor("#8ee7ff"), 3))
        body_color = QColor("#0f2940")
        if self._anger_level:
            body_color = QColor("#173149")
        painter.setBrush(body_color)
        painter.drawRoundedRect(
            int(center.x() - 58),
            int(center.y() + 52),
            116,
            70,
            24,
            24,
        )

        painter.setBrush(QColor("#133754"))
        chest = QPainterPath()
        chest.moveTo(center.x(), center.y() + 48)
        chest.cubicTo(
            center.x() - 18,
            center.y() + 70,
            center.x() - 14,
            center.y() + 102,
            center.x(),
            center.y() + 112,
        )
        chest.cubicTo(
            center.x() + 14,
            center.y() + 102,
            center.x() + 18,
            center.y() + 70,
            center.x(),
            center.y() + 48,
        )
        painter.drawPath(chest)

    def _draw_background_glow(self, painter: QPainter, center: QPointF) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(16, 84, 121, 90))
        painter.drawEllipse(center, 105, 105)
        painter.setBrush(QColor(30, 184, 216, 45))
        painter.drawEllipse(center, 72, 72)

    def _draw_data_lines(self, painter: QPainter, center: QPointF) -> None:
        pen = QPen(QColor("#1bc4e8"), 2)
        painter.setPen(pen)
        points = [
            QPointF(center.x() - 88, center.y() - 82),
            QPointF(center.x() - 56, center.y() - 104),
            QPointF(center.x(), center.y() - 122),
            QPointF(center.x() + 56, center.y() - 104),
            QPointF(center.x() + 88, center.y() - 82),
        ]
        painter.drawPolyline(points)
        for point in points:
            painter.setBrush(QColor("#1bc4e8"))
            painter.drawEllipse(point, 4, 4)

    def _draw_cat_head(self, painter: QPainter, center: QPointF) -> None:
        painter.setPen(QPen(QColor("#8ee7ff"), 3))
        head_color = QColor("#102d46")
        if self._anger_level:
            head_color = QColor(22 + self._anger_level * 6, 38, 56)
        painter.setBrush(head_color)
        head_path = QPainterPath()
        head_path.moveTo(center.x(), center.y() - 78)
        head_path.cubicTo(
            center.x() - 70,
            center.y() - 74,
            center.x() - 92,
            center.y() + 8,
            center.x() - 58,
            center.y() + 58,
        )
        head_path.cubicTo(
            center.x() - 38,
            center.y() + 84,
            center.x() + 38,
            center.y() + 84,
            center.x() + 58,
            center.y() + 58,
        )
        head_path.cubicTo(
            center.x() + 92,
            center.y() + 8,
            center.x() + 70,
            center.y() - 74,
            center.x(),
            center.y() - 78,
        )
        painter.drawPath(head_path)

        left_ear = QPainterPath()
        left_ear.moveTo(center.x() - 34, center.y() - 48)
        left_ear.lineTo(center.x() - 66, center.y() - 110)
        left_ear.lineTo(center.x() - 8, center.y() - 68)
        left_ear.closeSubpath()

        right_ear = QPainterPath()
        right_ear.moveTo(center.x() + 34, center.y() - 48)
        right_ear.lineTo(center.x() + 66, center.y() - 110)
        right_ear.lineTo(center.x() + 8, center.y() - 68)
        right_ear.closeSubpath()

        painter.drawPath(left_ear)
        painter.drawPath(right_ear)

        cheek_color = QColor("#173b59")
        if self._anger_level:
            cheek_color = QColor(54 + self._anger_level * 12, 46, 68)
        painter.setBrush(cheek_color)
        painter.drawEllipse(QPointF(center.x() - 34, center.y() + 18), 24, 20)
        painter.drawEllipse(QPointF(center.x() + 34, center.y() + 18), 24, 20)

        painter.setBrush(QColor("#133754"))
        painter.drawEllipse(QPointF(center.x(), center.y() + 28), 26, 22)

        self._draw_eyes(painter, center)
        self._draw_brows(painter, center)
        self._draw_nose_and_mouth(painter, center)
        self._draw_whiskers(painter, center)
        self._draw_lock(painter, center)

    def _draw_eyes(self, painter: QPainter, center: QPointF) -> None:
        eye_centers = [
            QPointF(center.x() - 28, center.y() - 2),
            QPointF(center.x() + 28, center.y() - 2),
        ]
        cursor_local = QPointF(self.mapFromGlobal(self.cursor().pos()))

        painter.setPen(QPen(QColor("#d7f8ff"), 2))
        for eye_center in eye_centers:
            painter.setBrush(QColor("#cffdff"))
            eye_path = QPainterPath()
            eye_path.moveTo(eye_center.x() - 15, eye_center.y())
            eye_path.quadTo(eye_center.x(), eye_center.y() - 11, eye_center.x() + 15, eye_center.y())
            eye_path.quadTo(eye_center.x(), eye_center.y() + 9, eye_center.x() - 15, eye_center.y())
            painter.drawPath(eye_path)

            vector_x = cursor_local.x() - eye_center.x()
            vector_y = cursor_local.y() - eye_center.y()
            distance = max((vector_x**2 + vector_y**2) ** 0.5, 1.0)
            offset = min(distance, 3.5)
            pupil_center = QPointF(
                eye_center.x() + (vector_x / distance) * offset,
                eye_center.y() + (vector_y / distance) * offset,
            )

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#08131f"))
            pupil_width = 3.5 + self._anger_level * 0.7
            pupil_height = 5.5 + self._anger_level * 1.4
            painter.drawEllipse(pupil_center, pupil_width, pupil_height)
            painter.setPen(QPen(QColor("#d7f8ff"), 2))

    def _draw_brows(self, painter: QPainter, center: QPointF) -> None:
        if not self._anger_level:
            return

        brow_pen = QPen(QColor("#ff7a7a"), 3 + self._anger_level * 0.3)
        brow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(brow_pen)
        painter.drawLine(
            QPointF(center.x() - 44, center.y() - 20 - self._anger_level),
            QPointF(center.x() - 14, center.y() - 12 + self._anger_level),
        )
        painter.drawLine(
            QPointF(center.x() + 44, center.y() - 20 - self._anger_level),
            QPointF(center.x() + 14, center.y() - 12 + self._anger_level),
        )

    def _draw_nose_and_mouth(self, painter: QPainter, center: QPointF) -> None:
        painter.setPen(
            QPen(
                QColor("#cffdff"),
                4,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        painter.setBrush(QColor("#1bc4e8"))
        nose = QPainterPath()
        nose.moveTo(center.x(), center.y() + 14)
        nose.lineTo(center.x() - 9, center.y() + 23)
        nose.lineTo(center.x() + 9, center.y() + 23)
        nose.closeSubpath()
        painter.drawPath(nose)
        painter.drawLine(
            QPointF(center.x(), center.y() + 23),
            QPointF(center.x(), center.y() + 34),
        )
        if self._anger_level:
            painter.drawArc(
                int(center.x() - 20),
                int(center.y() + 30),
                20,
                10,
                20 * 16,
                120 * 16,
            )
            painter.drawArc(
                int(center.x()),
                int(center.y() + 30),
                20,
                10,
                40 * 16,
                120 * 16,
            )
        else:
            painter.drawArc(
                int(center.x() - 19),
                int(center.y() + 26),
                20,
                14,
                210 * 16,
                110 * 16,
            )
            painter.drawArc(
                int(center.x() - 1),
                int(center.y() + 26),
                20,
                14,
                220 * 16,
                110 * 16,
            )

    def _draw_whiskers(self, painter: QPainter, center: QPointF) -> None:
        painter.setPen(QPen(QColor("#8ee7ff"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        whisker_y_positions = [center.y() + 18, center.y() + 28, center.y() + 38]
        for whisker_y in whisker_y_positions:
            painter.drawLine(
                QPointF(center.x() - 28, whisker_y),
                QPointF(center.x() - 82, whisker_y - 6),
            )
            painter.drawLine(
                QPointF(center.x() + 28, whisker_y),
                QPointF(center.x() + 82, whisker_y - 6),
            )

    def _draw_lock(self, painter: QPainter, center: QPointF) -> None:
        painter.setPen(QPen(QColor("#1bc4e8"), 3))
        painter.setBrush(QColor("#0a1725"))
        painter.drawRoundedRect(int(center.x() - 22), int(center.y() + 56), 44, 30, 8, 8)
        painter.drawArc(int(center.x() - 16), int(center.y() + 44), 32, 24, 0, 180 * 16)
        painter.setBrush(QColor("#1bc4e8"))
        painter.drawEllipse(QPointF(center.x(), center.y() + 69), 4, 4)


class LoginWindow(QWidget):
    """Login gate shown before the main password manager window."""

    def __init__(self) -> None:
        super().__init__()
        self.failed_attempts = 0
        self.main_window: PasswordManagerWindow | None = None

        self.setWindowTitle("SecretKitty Login")
        self.resize(520, 640)
        self.setFont(QFont("Segoe UI", 10))

        self.cat_widget = GuardianCatWidget()
        self.cat_widget.setMinimumSize(280, 280)
        self.status_label = QLabel("Enter the vault password to continue.")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Master password")
        self.password_input.returnPressed.connect(self._attempt_login)
        self.login_button = QPushButton("Unlock vault")
        self.login_button.clicked.connect(self._attempt_login)

        self._build_layout()
        self._apply_styles()

    def _build_layout(self) -> None:
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(40, 36, 40, 36)
        root_layout.setSpacing(18)

        card = QFrame()
        card.setObjectName("loginCard")
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(28, 28, 28, 28)
        card_layout.setSpacing(16)

        title_label = QLabel("SecretKitty")
        title_label.setObjectName("loginTitle")
        subtitle_label = QLabel("Secure access required before opening your vault.")
        subtitle_label.setObjectName("loginSubtitle")
        subtitle_label.setWordWrap(True)
        self.status_label.setObjectName("loginStatus")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        card_layout.addWidget(subtitle_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        card_layout.addWidget(self.cat_widget, alignment=Qt.AlignmentFlag.AlignHCenter)
        card_layout.addWidget(self.status_label)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(self.login_button)
        card.setLayout(card_layout)

        root_layout.addStretch()
        root_layout.addWidget(card)
        root_layout.addStretch()
        self.setLayout(root_layout)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background: #08131f;
                color: #d7e7f7;
            }
            QFrame#loginCard {
                background: #0f2234;
                border: 1px solid #1d4360;
                border-radius: 24px;
            }
            QLabel {
                color: #9cb7cf;
                background: transparent;
            }
            QLabel#loginTitle {
                color: #eef7ff;
                font-size: 30px;
                font-weight: 700;
            }
            QLabel#loginSubtitle {
                color: #9cb7cf;
                font-size: 14px;
            }
            QLabel#loginStatus {
                color: #cfe9ff;
                font-size: 13px;
                font-weight: 600;
                min-height: 24px;
            }
            QLineEdit {
                min-height: 42px;
                padding: 8px 12px;
                border-radius: 12px;
                border: 1px solid #2d5676;
                background: #081a2a;
                color: #eef7ff;
                selection-background-color: #17b8d8;
            }
            QLineEdit:focus {
                border: 2px solid #17b8d8;
            }
            QPushButton {
                min-height: 44px;
                border: none;
                border-radius: 14px;
                background: #1298c1;
                color: #f4fdff;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #0fb1da;
            }
            """
        )

    def _attempt_login(self) -> None:
        if self.password_input.text() == LOGIN_PASSWORD:
            self.main_window = PasswordManagerWindow(VAULT_PATH)
            self.main_window.show()
            self.close()
            return

        self.failed_attempts += 1
        self.cat_widget.set_anger_level(self.failed_attempts)
        self.status_label.setText("Wrong password. The guardian cat is not amused.")
        self.password_input.clear()
        self.password_input.setFocus()


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
        self.notes_input = QLineEdit()
        self.url_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.status_label = QLabel()
        self.detail_label = QLabel()
        self.sidebar_tree = QTreeWidget()
        self.search_input = QLineEdit()
        self.sidebar_card: QFrame | None = None
        self.sidebar_shell: QWidget | None = None
        self.new_entry_button = QPushButton("+")
        self.search_button = QPushButton("⌕")
        self.copy_password_button = QPushButton("Copy password")
        self.is_search_visible = False

        self._build_layout()
        self._apply_styles()
        self._set_search_visible(False)
        self._refresh_sidebar()
        self._set_status(f"Vault file: {self.vault_path.name}")

    def _apply_fonts(self) -> None:
        base_font = QFont("Segoe UI", 10)
        self.setFont(base_font)

    def _build_layout(self) -> None:
        shell_layout = QHBoxLayout()
        shell_layout.setContentsMargins(24, 24, 24, 24)
        shell_layout.setSpacing(18)

        self.sidebar_shell = self._build_sidebar_shell()
        shell_layout.addWidget(self.sidebar_shell, 2)
        shell_layout.addWidget(self._build_content_card(), 5)
        self.setLayout(shell_layout)

    def _build_sidebar_shell(self) -> QWidget:
        shell_widget = QWidget()
        shell_layout = QHBoxLayout()
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        self.sidebar_card = self._build_sidebar_card()
        shell_layout.addWidget(self.sidebar_card)
        shell_widget.setLayout(shell_layout)
        return shell_widget

    def _build_sidebar_card(self) -> QFrame:
        sidebar_card = QFrame()
        sidebar_card.setObjectName("sidebarCard")
        sidebar_card.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        sidebar_card.customContextMenuRequested.connect(
            self._handle_sidebar_context_menu
        )

        title_label = QLabel("Navigator")
        title_label.setObjectName("sectionTitle")
        subtitle_label = QLabel("Browse items in a tree view.")
        subtitle_label.setObjectName("sectionSubtitle")

        self.sidebar_tree.setHeaderHidden(True)
        self.sidebar_tree.setRootIsDecorated(True)
        self.sidebar_tree.setItemsExpandable(True)
        self.sidebar_tree.setIndentation(18)
        self.sidebar_tree.viewport().installEventFilter(self)
        self.sidebar_tree.itemSelectionChanged.connect(self._handle_tree_selection)
        self.sidebar_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.sidebar_tree.customContextMenuRequested.connect(
            self._handle_tree_context_menu
        )

        self.new_entry_button.setObjectName("navCircleButton")
        self.new_entry_button.clicked.connect(self._start_new_entry)
        self.search_button.setObjectName("navCircleButton")
        self.search_button.clicked.connect(self._toggle_search)

        self.search_input.setPlaceholderText("Search entries...")
        self.search_input.textChanged.connect(self._handle_search_changed)
        self.search_input.setClearButtonEnabled(True)

        header_row = QHBoxLayout()
        header_row.setSpacing(10)

        title_column = QVBoxLayout()
        title_column.setSpacing(4)
        title_column.addWidget(title_label)
        title_column.addWidget(subtitle_label)

        header_row.addLayout(title_column)
        header_row.addStretch()
        header_row.addWidget(self.search_button)
        header_row.addWidget(self.new_entry_button)

        layout = QVBoxLayout()
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)
        layout.addLayout(header_row)
        layout.addWidget(self.search_input)
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
            "A focused security console for browsing and protecting account secrets."
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
        art_layout.addWidget(GuardianCatWidget(), alignment=Qt.AlignmentFlag.AlignCenter)
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
        form_layout.addRow("Notes", self.notes_input)
        form_layout.addRow("URL", self.url_input)

        save_button = QPushButton("Save entry")
        save_button.clicked.connect(self._handle_save_entry)

        clear_button = QPushButton("Clear form")
        clear_button.setObjectName("secondaryButton")
        clear_button.clicked.connect(self._clear_form)

        self.copy_password_button.setObjectName("secondaryButton")
        self.copy_password_button.clicked.connect(self._copy_password)

        button_row = QHBoxLayout()
        button_row.addWidget(save_button)
        button_row.addWidget(self.copy_password_button)
        button_row.addWidget(clear_button)
        button_row.addStretch()

        wrapper_layout = QVBoxLayout()
        wrapper_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("Entry editor")
        title_label.setObjectName("sectionTitle")
        subtitle_label = QLabel(
            "Select an item on the left to inspect it, or register a new protected record here."
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
                background: #08131f;
                color: #d7e7f7;
            }
            QFrame#sidebarCard,
            QFrame#contentCard,
            QFrame#heroTextCard,
            QFrame#artCard,
            QFrame#formCard {
                background: #0f2234;
                border: 1px solid #1d4360;
                border-radius: 22px;
            }
            QFrame#sidebarCard {
                background: #0b1a29;
            }
            QFrame#heroTextCard {
                background: #10263b;
            }
            QFrame#artCard {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #102944,
                    stop: 0.55 #0d4f74,
                    stop: 1 #17b8d8
                );
            }
            QLabel#heroTitle {
                font-size: 30px;
                font-weight: 700;
                color: #eef7ff;
            }
            QLabel {
                color: #9cb7cf;
                background: transparent;
            }
            QLabel#sectionTitle {
                font-size: 18px;
                font-weight: 700;
                color: #dff4ff;
            }
            QPushButton#navCircleButton {
                min-width: 36px;
                max-width: 36px;
                min-height: 36px;
                max-height: 36px;
                padding: 0;
                border-radius: 18px;
                background: #143651;
                color: #f4fdff;
                font-size: 18px;
                font-weight: 700;
            }
            QPushButton#navCircleButton:hover {
                background: #1a4a6c;
            }
            QLineEdit {
                min-height: 40px;
                padding: 8px 12px;
                border-radius: 12px;
                border: 1px solid #2d5676;
                background: #081a2a;
                color: #eef7ff;
                selection-background-color: #17b8d8;
            }
            QLineEdit:focus {
                border: 2px solid #17b8d8;
            }
            QPushButton {
                min-height: 42px;
                padding: 0 18px;
                border: none;
                border-radius: 14px;
                background: #1298c1;
                color: #f4fdff;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #0fb1da;
            }
            QPushButton#secondaryButton {
                background: #183049;
                color: #bcd5ea;
            }
            QPushButton#secondaryButton:hover {
                background: #21425f;
            }
            QTreeWidget {
                background: #081a2a;
                border: 1px solid #1f4764;
                border-radius: 16px;
                padding: 6px;
                color: #d7e7f7;
                outline: 0;
                show-decoration-selected: 0;
            }
            QTreeWidget::item {
                min-height: 34px;
                border-radius: 10px;
                padding: 4px 10px;
            }
            QTreeWidget::branch,
            QTreeWidget::branch:selected {
                background: transparent;
            }
            QTreeWidget::item:hover {
                background: rgba(23, 184, 216, 0.16);
            }
            QTreeWidget::item:selected {
                background: rgba(23, 184, 216, 0.32);
                color: #f4fdff;
            }
            QTreeWidget::branch:closed:has-children {
                image: url(none);
            }
            QTreeWidget::branch:open:has-children {
                image: url(none);
            }
            """
        )

    def _handle_save_entry(self) -> None:
        title = self.title_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        notes = self.notes_input.text().strip()
        url = self.url_input.text().strip()

        if not title or not username or not password:
            QMessageBox.warning(self, "Missing fields", "Please fill all fields.")
            return

        saved_entry_id = self.selected_entry_id

        if self.selected_entry_id and self._find_entry_by_id(self.selected_entry_id):
            update_entry(
                self.selected_entry_id,
                title=title,
                username=username,
                password=password,
                notes=notes,
                url=url,
            )
            self.state = load_vault(self.vault_path)
            status_message = f"Saved '{title}'"
        else:
            add_entry(
                title=title,
                username=username,
                password=password,
                notes=notes,
                url=url,
            )
            self.state = load_vault(self.vault_path)
            if self.state.entries:
                saved_entry_id = self.state.entries[-1].get("id")
                if saved_entry_id is not None:
                    self.selected_entry_id = str(saved_entry_id)
            status_message = f"Created '{title}'"

        self._refresh_sidebar(selected_entry_id=saved_entry_id)
        self._set_status(f"{status_message} in {self.vault_path.name}")

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
        self.notes_input.setText(entry.get("notes", ""))
        self.url_input.setText(entry.get("url", ""))
        created_at = entry.get("created_at", "")
        self.detail_label.setText(
            f"Selected: {entry.get('title', 'Untitled')}\n"
            f"Username: {entry.get('username', '')}\n"
            f"Created: {created_at}"
        )

    def _copy_password(self) -> None:
        password = self.password_input.text()
        if not password:
            QMessageBox.information(
                self,
                "Nothing to copy",
                "The password field is empty.",
            )
            return

        clipboard = QApplication.clipboard()
        clipboard.setText(password)
        self._set_status("Password copied to clipboard")

    def _start_new_entry(self) -> None:
        self.selected_entry_id = None
        self.sidebar_tree.clearSelection()
        self._clear_form()
        self.search_input.clear()
        self._set_search_visible(False)
        self.detail_label.setText(
            "Creating a new entry. Fill the form and press Save entry."
        )
        self._set_status("New entry editor opened")

    def _focus_search(self) -> None:
        self.search_input.setFocus()
        self.search_input.selectAll()

    def _toggle_search(self) -> None:
        next_visible = not self.is_search_visible
        if self.is_search_visible and self.search_input.text().strip():
            self.search_input.clear()
        self._set_search_visible(next_visible)
        if next_visible:
            self._focus_search()

    def _set_search_visible(self, is_visible: bool) -> None:
        self.is_search_visible = is_visible
        self.search_input.setVisible(is_visible)
        self.search_button.setText("×" if is_visible else "⌕")

    def _handle_search_changed(self, _text: str) -> None:
        self._refresh_sidebar(selected_entry_id=self.selected_entry_id)

    def eventFilter(self, watched: object, event: QEvent) -> bool:
        if (
            watched is self.sidebar_tree.viewport()
            and event.type() == QEvent.Type.MouseButtonPress
            and self.sidebar_tree.itemAt(event.pos()) is None
        ):
            self._clear_tree_selection()
            return False

        return super().eventFilter(watched, event)

    def _handle_tree_context_menu(self, position) -> None:
        item = self.sidebar_tree.itemAt(position)
        global_position = self.sidebar_tree.viewport().mapToGlobal(position)
        self._show_navigator_context_menu(global_position, item)

    def _handle_sidebar_context_menu(self, position) -> None:
        if self.sidebar_card is None:
            return

        global_position = self.sidebar_card.mapToGlobal(position)
        tree_position = self.sidebar_tree.viewport().mapFromGlobal(global_position)
        item = self.sidebar_tree.itemAt(tree_position)
        self._show_navigator_context_menu(global_position, item)

    def _show_navigator_context_menu(
        self,
        global_position,
        item: QTreeWidgetItem | None,
    ) -> None:
        if item is not None:
            self.sidebar_tree.setCurrentItem(item)

        menu = QMenu(self)
        add_action = menu.addAction("Add entry")
        delete_action = menu.addAction("Delete entry")

        entry_id = None if item is None else item.data(0, Qt.ItemDataRole.UserRole)
        delete_action.setEnabled(entry_id is not None)

        selected_action = menu.exec(global_position)
        if selected_action == add_action:
            self._start_new_entry()
        elif selected_action == delete_action and entry_id is not None:
            self._delete_entry(str(entry_id))

    def _delete_entry(self, entry_id: str) -> None:
        entry = self._find_entry_by_id(entry_id)
        if entry is None:
            return

        confirm = QMessageBox.question(
            self,
            "Delete entry",
            f"Delete '{entry.get('title', 'Untitled')}'?",
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        delete_entry(entry_id)
        self.state = load_vault(self.vault_path)
        self.selected_entry_id = None
        self._clear_form()
        self._refresh_sidebar()
        self._set_status(f"Deleted '{entry.get('title', 'Untitled')}'")

    def _clear_tree_selection(self) -> None:
        self.sidebar_tree.clearSelection()
        self.sidebar_tree.setCurrentItem(None)
        self.selected_entry_id = None
        self._clear_form()
        self.detail_label.setText(
            "Creating a new entry. Fill the form and press Save entry."
        )
        self._set_status("Selection cleared. Ready to create a new entry")

    def _refresh_sidebar(self, selected_entry_id: str | None = None) -> None:
        self.sidebar_tree.clear()
        target_entry_id = selected_entry_id or self.selected_entry_id
        selected_item: QTreeWidgetItem | None = None
        search_term = self.search_input.text().strip().lower()

        root_item = QTreeWidgetItem(["All Entries"])
        root_item.setData(0, Qt.ItemDataRole.UserRole, None)
        self.sidebar_tree.addTopLevelItem(root_item)

        for entry in self.state.entries:
            if search_term:
                searchable_text = " ".join(
                    [
                        str(entry.get("title", "")),
                        str(entry.get("username", "")),
                    ]
                ).lower()
                if search_term not in searchable_text:
                    continue

            item = QTreeWidgetItem([build_entry_label(entry)])
            item.setData(0, Qt.ItemDataRole.UserRole, entry.get("id"))
            root_item.addChild(item)

            if entry.get("id") == target_entry_id:
                selected_item = item

        root_item.setExpanded(True)

        if selected_item is not None:
            self.sidebar_tree.setCurrentItem(selected_item)
        else:
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
        self.notes_input.clear()
        self.url_input.clear()
        self.title_input.setFocus()

    def _set_status(self, message: str) -> None:
        self.status_label.setText(message)


def main() -> int:
    """Start the standalone PySide6 desktop application."""
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())