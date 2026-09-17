from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QKeySequence
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
)

class KeyInputDialog(QDialog):
    """
    Modal dialog that prompts the user to press a key, capturing
    the exact key for shortcut binding.
    Properly sized with Salmon accent to avoid any text clipping.
    """
    def __init__(self, parent=None, current_key: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Pilih Tombol Shortcut")
        self.setMinimumSize(440, 230)
        self.resize(440, 230)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.captured_key: str = current_key

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("TEKAN TOMBOL PADA KEYBOARD", self)
        title.setObjectName("sectionHeader")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.key_display = QLabel(f"Tombol: {current_key}" if current_key else "Menunggu input tombol...", self)
        self.key_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.key_display.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: 700;
                color: #FFA094;
                background-color: #1e1e22;
                border: 1px solid #E06D5E;
                border-radius: 4px;
                padding: 10px 16px;
                min-height: 24px;
            }
        """)
        layout.addWidget(self.key_display)

        hint = QLabel("Tekan tombol keyboard apapun (misal: 1, 2, Q, W, Delete). Tekan Esc untuk batal.", self)
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #8e8e93; font-size: 11px; line-height: 1.4;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.cancel_btn = QPushButton("Batal", self)
        self.cancel_btn.setObjectName("secondaryBtn")
        self.cancel_btn.setMinimumHeight(32)
        self.cancel_btn.clicked.connect(self.reject)

        self.ok_btn = QPushButton("Gunakan Tombol Ini", self)
        self.ok_btn.setObjectName("startBtn")
        self.ok_btn.setMinimumHeight(32)
        self.ok_btn.setEnabled(bool(self.captured_key))
        self.ok_btn.clicked.connect(self.accept)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)
        layout.addLayout(btn_layout)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()

        if key == Qt.Key.Key_Escape:
            self.reject()
            return

        if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
            return

        key_str = self._key_to_string(event)
        if key_str:
            self.captured_key = key_str
            self.key_display.setText(f"Tombol: {self.captured_key}")
            self.key_display.setStyleSheet("""
                QLabel {
                    font-size: 15px;
                    font-weight: 700;
                    color: #FFA094;
                    background-color: #241819;
                    border: 1px solid #E06D5E;
                    border-radius: 4px;
                    padding: 10px 16px;
                    min-height: 24px;
                }
            """)
            self.ok_btn.setEnabled(True)

    def _key_to_string(self, event: QKeyEvent) -> str:
        key = event.key()
        
        special_keys = {
            Qt.Key.Key_Delete: "Delete",
            Qt.Key.Key_Backspace: "Backspace",
            Qt.Key.Key_Space: "Space",
            Qt.Key.Key_Tab: "Tab",
            Qt.Key.Key_Return: "Enter",
            Qt.Key.Key_Enter: "Enter",
            Qt.Key.Key_Insert: "Insert",
            Qt.Key.Key_Home: "Home",
            Qt.Key.Key_End: "End",
            Qt.Key.Key_PageUp: "PageUp",
            Qt.Key.Key_PageDown: "PageDown",
        }
        if key in special_keys:
            return special_keys[key]

        if Qt.Key.Key_F1 <= key <= Qt.Key.Key_F12:
            return f"F{key - Qt.Key.Key_F1 + 1}"

        text = event.text().strip().upper()
        if text and text.isprintable():
            return text

        seq = QKeySequence(key).toString()
        return seq.upper() if seq else ""

    @classmethod
    def get_key(cls, parent=None, current_key: str = "") -> tuple[str, bool]:
        dialog = cls(parent, current_key)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            return dialog.captured_key, True
        return current_key, False
