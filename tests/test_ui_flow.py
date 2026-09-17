import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent

# Initialize QApplication for tests
app = QApplication.instance() or QApplication(["ui_test"])

from main import MainWindow
from ui.setup_view import SetupView
from ui.viewer_view import ViewerView

class TestUIFlow(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, "raw_photos")
        self.dest_dir = os.path.join(self.temp_dir, "sorted_photos")
        os.makedirs(self.source_dir, exist_ok=True)
        os.makedirs(self.dest_dir, exist_ok=True)

        # Create 3 test photos
        self.photo_paths = []
        for i in range(1, 4):
            path = os.path.join(self.source_dir, f"DSC_{i:04d}.JPG")
            img = Image.new("RGB", (400, 300), color=(i * 60, 100, 150))
            img.save(path, "JPEG")
            self.photo_paths.append(path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_setup_view_bindings(self):
        setup = SetupView()
        setup.src_input.setText(self.source_dir)
        setup.dest_input.setText(self.dest_dir)

        # Check that photos were detected
        setup._check_source_photos(self.source_dir)
        self.assertIn("3 foto", setup.src_info_lbl.text())

        # Test adding a shortcut row
        initial_rows = setup.table.rowCount()
        setup._add_row_item("9", "Custom_Folder", "Keterangan Uji")
        self.assertEqual(setup.table.rowCount(), initial_rows + 1)

        # Verify bindings extraction
        bindings = setup._get_current_bindings()
        self.assertIn("9", bindings)
        self.assertEqual(bindings["9"]["folder"], "Custom_Folder")

    def test_viewer_sort_and_counter_flow(self):
        viewer = ViewerView()
        session_config = {
            "source_dir": self.source_dir,
            "dest_root": self.dest_dir,
            "mode": "move",
            "duplicate_strategy": "rename",
            "bindings": {
                "1": {"folder": "Close_Up", "label": "Foto Close Up"},
                "2": {"folder": "Foto_Bareng", "label": "Group Photos"}
            },
            "image_files": list(self.photo_paths)
        }
        viewer.start_session(session_config)

        self.assertEqual(viewer.total_photos, 3)
        self.assertEqual(viewer.current_index, 0)
        # Check initial counter: Foto 1 / 3
        self.assertIn("Foto 1 / 3", viewer.info_label.text())
        self.assertIn("DSC_0001.JPG", viewer.info_label.text())

        # 1. Simulate pressing key '1' (Move to Close_Up)
        event_key1 = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_1, Qt.KeyboardModifier.NoModifier, "1")
        viewer.keyPressEvent(event_key1)

        # Counter MUST advance to Foto 2 / 3!
        self.assertEqual(viewer.current_index, 1)
        self.assertIn("Foto 2 / 3", viewer.info_label.text())
        self.assertIn("DSC_0002.JPG", viewer.info_label.text())
        self.assertEqual(viewer.history_manager.get_history_count(), 1)

        # 2. Simulate pressing Space (Skip)
        event_space = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Space, Qt.KeyboardModifier.NoModifier, " ")
        viewer.keyPressEvent(event_space)

        # Counter MUST advance to Foto 3 / 3!
        self.assertEqual(viewer.current_index, 2)
        self.assertIn("Foto 3 / 3", viewer.info_label.text())
        self.assertIn("DSC_0003.JPG", viewer.info_label.text())
        self.assertEqual(viewer.history_manager.get_history_count(), 2)

        # 3. Simulate Undo (Ctrl+Z)
        event_undo = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)
        viewer.keyPressEvent(event_undo)

        # Undo returns counter to Foto 2 / 3 (DSC_0002.JPG)
        self.assertEqual(viewer.current_index, 1)
        self.assertIn("Foto 2 / 3", viewer.info_label.text())
        self.assertIn("DSC_0002.JPG", viewer.info_label.text())
        self.assertEqual(viewer.history_manager.get_history_count(), 1)

        # 4. Simulate Undo again (Undo move of DSC_0001.JPG)
        viewer.keyPressEvent(event_undo)

        # Counter returns to Foto 1 / 3 (DSC_0001.JPG)
        self.assertEqual(viewer.current_index, 0)
        self.assertIn("Foto 1 / 3", viewer.info_label.text())
        self.assertIn("DSC_0001.JPG", viewer.info_label.text())
        self.assertEqual(viewer.history_manager.get_history_count(), 0)

        # Clean shutdown of worker threads
        viewer.file_worker.stop()
        viewer.image_loader.stop()

    def test_main_window_state_switching(self):
        window = MainWindow()
        self.assertEqual(window.stack.currentIndex(), 0)

        session_config = {
            "source_dir": self.source_dir,
            "dest_root": self.dest_dir,
            "mode": "move",
            "duplicate_strategy": "rename",
            "bindings": {
                "1": {"folder": "Close_Up", "label": "Foto Close Up"}
            },
            "image_files": list(self.photo_paths)
        }

        # Trigger start sorting
        window._on_start_sorting(session_config)
        self.assertEqual(window.stack.currentIndex(), 1)

        # Trigger exit back to setup
        window._on_exit_to_setup()
        self.assertEqual(window.stack.currentIndex(), 0)

        window.viewer_view.file_worker.stop()
        window.viewer_view.image_loader.stop()

if __name__ == "__main__":
    unittest.main()
