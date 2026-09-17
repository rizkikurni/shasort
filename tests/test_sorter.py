import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path
from PIL import Image

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.config_manager import ConfigManager
from core.file_worker import FileWorker, FileActionTask
from core.image_loader import ImageLoader
from core.history_manager import HistoryManager
from PyQt6.QtWidgets import QApplication

# Initialize headless/GUI application instance for Qt pixmap support
app = QApplication.instance() or QApplication(["test_app"])

class TestCoreModules(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, "source")
        self.dest_dir = os.path.join(self.temp_dir, "dest")
        os.makedirs(self.source_dir, exist_ok=True)
        os.makedirs(self.dest_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_presets_and_config(self):
        presets = ConfigManager.list_presets()
        self.assertGreaterEqual(len(presets), 3)
        stems = [p["file_stem"] for p in presets]
        self.assertIn("wedding", stems)
        self.assertIn("travel", stems)
        self.assertIn("street", stems)

        wedding_data = ConfigManager.load_preset("wedding")
        self.assertEqual(wedding_data.get("profile_name"), "Wedding Sorter")
        self.assertIn("1", wedding_data.get("bindings", {}))

        valid, msg = ConfigManager.validate_profile(wedding_data)
        self.assertTrue(valid, msg)

    def test_history_manager(self):
        hm = HistoryManager()
        self.assertFalse(hm.can_undo())

        hm.record_action("src/1.jpg", "dest/Close_Up/1.jpg", "move", 0, "Close_Up")
        hm.record_action("src/2.jpg", "dest/Foto_Bareng/2.jpg", "move", 1, "Foto_Bareng")
        hm.record_action("src/3.jpg", None, "skip", 2, "")

        self.assertEqual(hm.get_history_count(), 3)
        self.assertTrue(hm.can_undo())

        stats = hm.get_summary_stats()
        self.assertEqual(stats["total_processed"], 3)
        self.assertEqual(stats["skipped"], 1)
        self.assertEqual(stats["by_subfolder"]["Close_Up"], 1)
        self.assertEqual(stats["by_subfolder"]["Foto_Bareng"], 1)

        last = hm.pop_last_action()
        self.assertEqual(last["action_type"], "skip")
        self.assertEqual(hm.get_history_count(), 2)

    def test_collision_resolution(self):
        worker = FileWorker()
        subfolder = Path(self.dest_dir) / "Sub"
        subfolder.mkdir(parents=True, exist_ok=True)

        target1 = worker.resolve_target_collision(subfolder, "photo.jpg", "rename")
        self.assertEqual(target1.name, "photo.jpg")

        # Create target1
        target1.touch()
        target2 = worker.resolve_target_collision(subfolder, "photo.jpg", "rename")
        self.assertEqual(target2.name, "photo_1.jpg")

        target2.touch()
        target3 = worker.resolve_target_collision(subfolder, "photo.jpg", "rename")
        self.assertEqual(target3.name, "photo_2.jpg")

    def test_image_loader_metadata(self):
        test_img_path = os.path.join(self.source_dir, "test_pic.jpg")
        img = Image.new("RGB", (800, 600), color=(100, 150, 200))
        img.save(test_img_path, "JPEG")

        data = ImageLoader.load_image_from_disk(test_img_path)
        self.assertIsNone(data.error)
        self.assertEqual(data.width, 800)
        self.assertEqual(data.height, 600)
        self.assertAlmostEqual(data.megapixels, 0.5, delta=0.1)
        self.assertGreater(data.filesize_bytes, 0)

    def test_file_worker_execution(self):
        worker = FileWorker()
        src_file = os.path.join(self.source_dir, "pic1.jpg")
        with open(src_file, "w") as f:
            f.write("content")

        subfolder = os.path.join(self.dest_dir, "Close_Up")
        
        # Test move
        task_move = FileActionTask("move", src_file, subfolder, 0, "rename")
        worker._process_task(task_move)
        
        expected_target = os.path.join(subfolder, "pic1.jpg")
        self.assertFalse(os.path.exists(src_file))
        self.assertTrue(os.path.exists(expected_target))

        # Test revert move (undo)
        task_undo = FileActionTask("revert_move", expected_target, self.source_dir, 0, explicit_target_path=src_file)
        worker._process_task(task_undo)
        self.assertTrue(os.path.exists(src_file))
        self.assertFalse(os.path.exists(expected_target))

if __name__ == "__main__":
    unittest.main()
