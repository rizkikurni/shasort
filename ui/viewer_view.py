import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent, QPixmap, QResizeEvent
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
)

from core.image_loader import ImageLoader, ImageData
from core.file_worker import FileWorker, FileActionTask
from core.history_manager import HistoryManager
from ui.widgets.hud_overlay import HUDOverlay
from ui.widgets.floating_toast import FloatingToast
from ui.summary_dialog import SummaryDialog

class PhotoCanvas(QLabel):
    """
    Dedicated widget for displaying images with smooth aspect-ratio scaling
    and zero letterboxing distortion.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: #121214;")
        self._current_pixmap: Optional[QPixmap] = None
        self._placeholder_text: str = "Memuat foto..."

    def set_pixmap(self, pixmap: Optional[QPixmap]):
        self._current_pixmap = pixmap
        self._update_display()

    def set_placeholder(self, text: str):
        self._current_pixmap = None
        self._placeholder_text = text
        self.setText(text)
        self.setStyleSheet("background-color: #121214; color: #71717a; font-size: 14px;")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_display()

    def _update_display(self):
        if self._current_pixmap and not self._current_pixmap.isNull():
            scaled = self._current_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            super().setPixmap(scaled)
        elif self._placeholder_text:
            self.setText(self._placeholder_text)


class ViewerView(QWidget):
    """
    Action View (Focus Mode): Full-screen / auto-fit minimalist photo viewer
    with keyboard event interception, HUD overlay, top-right floating toast,
    and 0ms latency preloading.
    Professional matte dark aesthetic with Salmon accents.
    """
    exit_to_setup = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("viewerView")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Session data
        self.session_config: Dict[str, Any] = {}
        self.photo_list: List[str] = []
        self.total_photos: int = 0
        self.current_index: int = 0
        self.photo_status: Dict[int, Dict[str, Any]] = {}

        # Subsystems
        self.image_loader = ImageLoader(max_cache_size=20, parent=self)
        self.file_worker = FileWorker(parent=self)
        self.history_manager = HistoryManager()

        # Connect background worker signals
        self.file_worker.task_completed.connect(self._on_file_task_completed)
        self.file_worker.task_failed.connect(self._on_file_task_failed)
        self.file_worker.start()

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 10, 14, 12)
        main_layout.setSpacing(6)

        # 1. Top Header Bar
        header_bar = QHBoxLayout()
        header_bar.setContentsMargins(6, 0, 6, 0)

        self.info_label = QLabel("Foto 0 / 0", self)
        self.info_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 600;
                color: #e4e4e7;
                letter-spacing: 0.3px;
            }
        """)
        header_bar.addWidget(self.info_label)
        header_bar.addStretch()

        self.exit_btn = QPushButton("Keluar (Esc)", self)
        self.exit_btn.setObjectName("secondaryBtn")
        self.exit_btn.setFixedSize(96, 28)
        self.exit_btn.clicked.connect(self._confirm_exit)
        header_bar.addWidget(self.exit_btn)

        main_layout.addLayout(header_bar)

        # 2. Main Photo Display Canvas
        self.canvas = PhotoCanvas(self)
        main_layout.addWidget(self.canvas, stretch=1)

        # 3. Bottom HUD Overlay Bar (clean key list, no toast)
        self.hud = HUDOverlay(self)
        main_layout.addWidget(self.hud, alignment=Qt.AlignmentFlag.AlignCenter)

        # 4. Floating Toast Notification in top-right corner
        self.toast = FloatingToast(self)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self.toast.reposition()

    def start_session(self, session_config: Dict[str, Any]):
        """Initializes and activates Focus Sorter session with given configuration."""
        self.session_config = session_config
        self.photo_list = list(session_config.get("image_files", []))
        self.total_photos = len(self.photo_list)
        self.current_index = 0
        self.photo_status.clear()

        self.history_manager.clear()
        self.image_loader.clear()

        # Update HUD active bindings
        bindings = self.session_config.get("bindings", {})
        self.hud.update_bindings(bindings)

        self.setFocus()
        self._load_current_image()

    def _load_current_image(self):
        """Displays image at current_index and preloads adjacent images into RAM."""
        if self.total_photos == 0:
            self._on_sorting_completed()
            return

        if self.current_index >= self.total_photos:
            self._on_sorting_completed()
            return

        if self.current_index < 0:
            self.current_index = 0

        current_path = self.photo_list[self.current_index]

        # If file was moved to a subfolder, get its actual current path
        status_info = self.photo_status.get(self.current_index)
        effective_path = current_path
        if status_info and status_info.get("target_path") and os.path.exists(status_info["target_path"]):
            effective_path = status_info["target_path"]

        # Fetch image from cache (or disk)
        img_data: ImageData = self.image_loader.get_image(effective_path)

        if img_data.error:
            self.canvas.set_placeholder(f"Gagal memuat: {img_data.error}\n({Path(current_path).name})")
        elif img_data.pixmap:
            self.canvas.set_pixmap(img_data.pixmap)
        else:
            self.canvas.set_placeholder("Memuat foto...")

        # Update Header Info Bar with Salmon counter: Foto 1 / 30
        mp_text = f"{img_data.megapixels} MP" if img_data.megapixels > 0 else "Resolusi -"
        size_text = f"{img_data.filesize_mb} MB" if img_data.filesize_mb > 0 else "- MB"
        
        status_tag = ""
        if status_info:
            if status_info.get("action") == "move":
                status_tag = f"   <span style='color: #FFA094;'>[Dipindah: {status_info.get('subfolder')}]</span>"
            elif status_info.get("action") == "copy":
                status_tag = f"   <span style='color: #60a5fa;'>[Disalin: {status_info.get('subfolder')}]</span>"
            elif status_info.get("action") == "skip":
                status_tag = "   <span style='color: #71717a;'>[Dilewati]</span>"

        self.info_label.setText(
            f"<span style='color: #FFA094; font-weight: 700;'>Foto {self.current_index + 1} / {self.total_photos}</span>   |   "
            f"{Path(current_path).name}   ({mp_text}, {size_text}){status_tag}"
        )

        # Preload next 2 photos and previous 1 photo into RAM for 0ms transition
        preload_paths = []
        if self.current_index + 1 < self.total_photos:
            preload_paths.append(self.photo_list[self.current_index + 1])
        if self.current_index + 2 < self.total_photos:
            preload_paths.append(self.photo_list[self.current_index + 2])
        if self.current_index - 1 >= 0:
            preload_paths.append(self.photo_list[self.current_index - 1])

        self.image_loader.preload(preload_paths)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()

        # 1. Escape: Exit Focus Mode
        if key == Qt.Key.Key_Escape:
            self._confirm_exit()
            return

        # 2. Undo: Ctrl+Z or Backspace
        if (event.modifiers() == Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_Z) or key == Qt.Key.Key_Backspace:
            self._handle_undo()
            return

        # 3. Manual Navigation: A or Left Arrow (Previous)
        if key in (Qt.Key.Key_A, Qt.Key.Key_Left):
            self._navigate(-1)
            return

        # 4. Manual Navigation: D or Right Arrow (Next)
        if key in (Qt.Key.Key_D, Qt.Key.Key_Right):
            self._navigate(1)
            return

        # 5. Skip: Spacebar
        if key == Qt.Key.Key_Space:
            self._handle_skip()
            return

        # 6. Keybindings check (1..9, letters, Delete, etc.)
        matched_binding = self._match_keybinding(event)
        if matched_binding:
            key_name, info = matched_binding
            self._handle_sort_action(key_name, info)
            return

        super().keyPressEvent(event)

    def _match_keybinding(self, event: QKeyEvent) -> Optional[tuple]:
        """Matches pressed key with user-configured bindings."""
        bindings = self.session_config.get("bindings", {})
        key = event.key()

        candidates = []
        if key == Qt.Key.Key_Delete:
            candidates.append("DELETE")
        elif Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
            candidates.append(chr(key))
        
        text = event.text().strip().upper()
        if text:
            candidates.append(text)

        for c in candidates:
            for b_key, b_info in bindings.items():
                if str(b_key).strip().upper() == c:
                    return b_key, b_info
        return None

    def _handle_sort_action(self, key_name: str, binding_info: Dict[str, Any]):
        """Executes move/copy action asynchronously and advances instantly."""
        if self.current_index >= self.total_photos:
            return

        current_path = self.photo_list[self.current_index]
        subfolder = binding_info.get("folder", "Unsorted")
        dest_root = self.session_config.get("dest_root", "")
        target_dir = os.path.join(dest_root, subfolder)
        mode = self.session_config.get("mode", "move")
        strategy = self.session_config.get("duplicate_strategy", "rename")

        # Top-right floating feedback toast
        action_verb = "Dipindah" if mode == "move" else "Disalin"
        self.toast.show_message(f"[{key_name}] {action_verb} ke: {subfolder}", toast_type="success")

        # Submit background I/O task
        task = FileActionTask(
            action_type=mode,
            source_path=current_path,
            target_dir=target_dir,
            image_index=self.current_index,
            duplicate_strategy=strategy
        )
        self.file_worker.submit_task(task)

        # Record action in history stack for Undo
        self.history_manager.record_action(
            source_path=current_path,
            target_path=None,
            action_type=mode,
            image_index=self.current_index,
            target_subfolder=subfolder
        )

        # Mark photo status and advance counter (e.g. 1/30 -> 2/30 -> 3/30)
        self.photo_status[self.current_index] = {
            "action": mode,
            "subfolder": subfolder,
            "target_dir": target_dir,
            "target_path": None
        }

        # Advance to next photo
        self.current_index += 1
        self._load_current_image()

    def _handle_skip(self):
        """Skips current photo without file action and advances to next."""
        if self.current_index >= self.total_photos:
            return

        current_path = self.photo_list[self.current_index]
        self.history_manager.record_action(
            source_path=current_path,
            target_path=None,
            action_type="skip",
            image_index=self.current_index,
            target_subfolder=""
        )
        self.photo_status[self.current_index] = {"action": "skip"}
        self.toast.show_message("Dilewati", toast_type="skip")
        
        self.current_index += 1
        self._load_current_image()

    def _handle_undo(self):
        """Reverts the last move/copy/skip action and jumps back to that photo."""
        if not self.history_manager.can_undo():
            self.toast.show_message("Tidak ada aksi untuk dibatalkan", toast_type="skip")
            return

        last_action = self.history_manager.pop_last_action()
        if not last_action:
            return

        action_type = last_action["action_type"]
        src_path = last_action["source_path"]
        orig_index = last_action["image_index"]

        if orig_index in self.photo_status:
            del self.photo_status[orig_index]

        if action_type == "skip":
            self.current_index = max(0, orig_index)
            self.toast.show_message("Undo: Batal lewati", toast_type="undo")
            self._load_current_image()
            return

        elif action_type == "move":
            target_path = last_action.get("target_path")
            target_subfolder = last_action.get("target_subfolder", "")
            dest_root = self.session_config.get("dest_root", "")
            expected_dest = target_path or os.path.join(dest_root, target_subfolder, Path(src_path).name)

            task = FileActionTask(
                action_type="revert_move",
                source_path=expected_dest,
                target_dir=os.path.dirname(src_path),
                image_index=orig_index,
                explicit_target_path=src_path
            )
            self.file_worker.submit_task(task)

            self.current_index = max(0, orig_index)
            self.toast.show_message(f"Undo: {Path(src_path).name} dipulihkan", toast_type="undo")
            self._load_current_image()

        elif action_type == "copy":
            target_path = last_action.get("target_path")
            target_subfolder = last_action.get("target_subfolder", "")
            dest_root = self.session_config.get("dest_root", "")
            expected_dest = target_path or os.path.join(dest_root, target_subfolder, Path(src_path).name)

            task = FileActionTask(
                action_type="revert_copy",
                source_path=expected_dest,
                target_dir="",
                image_index=orig_index,
                explicit_target_path=expected_dest
            )
            self.file_worker.submit_task(task)

            self.current_index = max(0, orig_index)
            self.toast.show_message(f"Undo: Salinan {Path(src_path).name} dihapus", toast_type="undo")
            self._load_current_image()

    def _navigate(self, delta: int):
        new_idx = self.current_index + delta
        if 0 <= new_idx < self.total_photos:
            self.current_index = new_idx
            self._load_current_image()

    def _on_file_task_completed(self, result: Dict[str, Any]):
        """Updates last action record with confirmed target_path."""
        src = result.get("source_path")
        target = result.get("target_path")
        idx = result.get("image_index")
        if idx is not None and idx in self.photo_status:
            self.photo_status[idx]["target_path"] = target

        if target:
            last = self.history_manager.peek_last_action()
            if last and last.get("source_path") == src and not last.get("target_path"):
                last["target_path"] = target

    def _on_file_task_failed(self, error_info: Dict[str, Any]):
        err = error_info.get("error", "Error tidak dikenal")
        self.toast.show_message(f"Gagal: {err}", toast_type="error")

    def _on_sorting_completed(self):
        """Displays completion summary dialog."""
        stats = self.history_manager.get_summary_stats()
        dest_root = self.session_config.get("dest_root", "")
        dialog = SummaryDialog(self, summary_stats=stats, dest_root=dest_root)
        dialog.exec()
        self.exit_to_setup.emit()

    def _confirm_exit(self):
        """Confirms exiting back to setup view."""
        if self.history_manager.get_history_count() > 0:
            reply = QMessageBox.question(
                self, "Konfirmasi Keluar",
                "Apakah Anda ingin mengakhiri sesi sortir dan melihat ringkasan hasil?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._on_sorting_completed()
                return

        self.exit_to_setup.emit()
