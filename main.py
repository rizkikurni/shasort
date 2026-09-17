import sys
import os
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout
)
from PyQt6.QtGui import QIcon, QFont

from ui.styles import DARK_THEME_QSS
from ui.setup_view import SetupView
from ui.viewer_view import ViewerView

class MainWindow(QMainWindow):
    """
    Main application controller managing dual-state transitions
    between Setup View and Action Focus View.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShaSort")
        self.resize(1050, 720)
        self.setMinimumSize(850, 600)

        # Central stacked widget for Dual-State Screen
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        # State 1: Setup View
        self.setup_view = SetupView(self)
        self.setup_view.start_sorting.connect(self._on_start_sorting)
        self.stack.addWidget(self.setup_view)

        # State 2: Focus Sorter View
        self.viewer_view = ViewerView(self)
        self.viewer_view.exit_to_setup.connect(self._on_exit_to_setup)
        self.stack.addWidget(self.viewer_view)

        # Start on Setup View
        self.stack.setCurrentIndex(0)

    def _on_start_sorting(self, session_config: dict):
        """Transitions from Setup View to Action Focus View."""
        self.viewer_view.start_session(session_config)
        self.stack.setCurrentIndex(1)
        self.viewer_view.setFocus()

    def _on_exit_to_setup(self):
        """Transitions back to Setup View and refreshes available photo count."""
        self.stack.setCurrentIndex(0)
        # Trigger scan refresh on source directory
        src_path = self.setup_view.src_input.text()
        self.setup_view._check_source_photos(src_path)

    def closeEvent(self, event):
        """Cleanly stops background threads before quitting."""
        try:
            self.viewer_view.file_worker.stop()
            self.viewer_view.image_loader.stop()
        except Exception as e:
            print(f"Error during shutdown: {e}")
        event.accept()


def main():
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 9))
    app.setStyleSheet(DARK_THEME_QSS)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
