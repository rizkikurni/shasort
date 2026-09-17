from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QFrame, QLabel, QHBoxLayout, QGraphicsOpacityEffect

class FloatingToast(QFrame):
    """
    Floating notification toast placed in the top-right corner of the viewer.
    Clean, sleek, with salmon/status accents and no blocking UI.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("floatingToast")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(8)

        self.label = QLabel("", self)
        self.label.setStyleSheet("font-size: 12px; font-weight: 600; background: transparent; border: none;")
        layout.addWidget(self.label)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

        self.hide()

    def show_message(self, text: str, toast_type: str = "success"):
        """Displays floating toast in the top-right corner."""
        # Color schemes with Salmon theme
        colors = {
            "success": {
                "border": "#E06D5E",      # Salmon
                "text": "#FFA094",        # Light Salmon
                "bg": "#1e1e24"
            },
            "undo": {
                "border": "#F59E0B",      # Amber
                "text": "#FCD34D",
                "bg": "#1e1e24"
            },
            "skip": {
                "border": "#71717A",      # Muted Zinc
                "text": "#D4D4D8",
                "bg": "#1e1e24"
            },
            "error": {
                "border": "#EF4444",      # Red
                "text": "#FCA5A5",
                "bg": "#1e1e24"
            }
        }
        style_cfg = colors.get(toast_type, colors["success"])

        self.setStyleSheet(f"""
            QFrame#floatingToast {{
                background-color: {style_cfg['bg']};
                border: 1px solid #323238;
                border-left: 3px solid {style_cfg['border']};
                border-radius: 4px;
            }}
        """)
        self.label.setStyleSheet(f"""
            QLabel {{
                color: {style_cfg['text']};
                font-size: 12px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        self.label.setText(text)
        self.adjustSize()
        self.reposition()
        self.show()
        self.raise_()
        self._timer.start(1800)

    def reposition(self):
        """Positions toast in top-right corner, neatly below header bar."""
        if self.parent():
            parent_w = self.parent().width()
            x = parent_w - self.width() - 20
            y = 48
            self.move(x, y)
