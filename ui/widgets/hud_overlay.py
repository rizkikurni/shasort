from typing import Dict, Any
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)

class HUDOverlay(QFrame):
    """
    Clean, low-profile bottom HUD overlay displaying active shortcut keybindings.
    Styled with Salmon accents.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setObjectName("hudOverlay")
        self.setStyleSheet("""
            QFrame#hudOverlay {
                background-color: #161619;
                border: 1px solid #27272a;
                border-radius: 6px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 8, 14, 8)
        main_layout.setSpacing(4)

        self.shortcuts_container = QWidget(self)
        self.shortcuts_layout = QVBoxLayout(self.shortcuts_container)
        self.shortcuts_layout.setContentsMargins(0, 0, 0, 0)
        self.shortcuts_layout.setSpacing(4)
        main_layout.addWidget(self.shortcuts_container)

    def update_bindings(self, bindings: Dict[str, Any]):
        """Renders clean key tags for user keybindings."""
        while self.shortcuts_layout.count():
            item = self.shortcuts_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(6)
        row1_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(6)
        row2_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        items = list(bindings.items())
        total = len(items)
        max_per_row = 5 if total > 5 else 6

        for i, (key, info) in enumerate(items):
            folder_name = info.get("folder", "")
            badge = self._create_badge(key, folder_name)
            if i < max_per_row:
                row1_layout.addWidget(badge)
            else:
                row2_layout.addWidget(badge)

        row1_widget = QWidget()
        row1_widget.setLayout(row1_layout)
        self.shortcuts_layout.addWidget(row1_widget)

        if row2_layout.count() > 0:
            row2_widget = QWidget()
            row2_widget.setLayout(row2_layout)
            self.shortcuts_layout.addWidget(row2_widget)

        # Built-in control bar
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ctrl_badges = [
            ("Space", "Lewati"),
            ("Ctrl+Z", "Undo"),
            ("A / D", "Navigasi"),
            ("Esc", "Setup")
        ]
        for key, desc in ctrl_badges:
            badge = self._create_badge(key, desc, is_system=True)
            controls_layout.addWidget(badge)

        ctrl_widget = QWidget()
        ctrl_widget.setLayout(controls_layout)
        self.shortcuts_layout.addWidget(ctrl_widget)

    def _create_badge(self, key: str, label: str, is_system: bool = False) -> QWidget:
        badge = QFrame()
        bg_col = "#202024" if not is_system else "#1a1a1d"
        border_col = "#333338" if not is_system else "#26262b"
        text_col = "#e4e4e7" if not is_system else "#8e8e93"
        key_color = "#FFA094" if not is_system else "#a1a1aa"  # Salmon accent for custom keys

        badge.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_col};
                border: 1px solid {border_col};
                border-radius: 3px;
                padding: 1px 4px;
            }}
        """)
        layout = QHBoxLayout(badge)
        layout.setContentsMargins(4, 2, 6, 2)
        layout.setSpacing(5)

        key_lbl = QLabel(f"[{key.upper()}]", badge)
        key_lbl.setStyleSheet(f"""
            QLabel {{
                color: {key_color};
                font-weight: 700;
                font-size: 11px;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(key_lbl)

        desc_lbl = QLabel(label, badge)
        desc_lbl.setStyleSheet(f"""
            QLabel {{
                color: {text_col};
                font-size: 11px;
                font-weight: 500;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(desc_lbl)

        return badge
