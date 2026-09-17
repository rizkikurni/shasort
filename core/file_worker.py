import os
import shutil
import queue
from pathlib import Path
from typing import Dict, Any, Optional
from PyQt6.QtCore import QThread, pyqtSignal, QObject

class FileActionTask:
    """Represents a single file move/copy or revert task."""
    def __init__(self, action_type: str, source_path: str, target_dir: str, 
                 image_index: int, duplicate_strategy: str = "rename",
                 explicit_target_path: Optional[str] = None):
        self.action_type = action_type.lower()  # "move", "copy", or "revert_move", "revert_copy"
        self.source_path = source_path
        self.target_dir = target_dir
        self.image_index = image_index
        self.duplicate_strategy = duplicate_strategy.lower() # "rename", "overwrite", "skip"
        self.explicit_target_path = explicit_target_path

class FileWorker(QThread):
    """
    Background worker that executes disk I/O operations (move, copy, undo)
    without freezing the main UI thread.
    """
    task_completed = pyqtSignal(dict)  # Emits action result dictionary
    task_failed = pyqtSignal(dict)     # Emits error dictionary
    queue_empty = pyqtSignal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._queue = queue.Queue()
        self._running = True

    def submit_task(self, task: FileActionTask):
        """Adds a task to the background processing queue."""
        self._queue.put(task)

    def stop(self):
        """Signals worker to finish and stop."""
        self._running = False
        self._queue.put(None)  # Sentinel to unblock get()
        self.wait(2000)

    def resolve_target_collision(self, dest_dir: Path, filename: str, strategy: str) -> Optional[Path]:
        """Resolves duplicate file collisions based on strategy."""
        target = dest_dir / filename
        if not target.exists():
            return target

        if strategy == "overwrite":
            return target
        elif strategy == "skip":
            return None
        else:
            # "rename" strategy: append _1, _2, etc.
            stem = target.stem
            suffix = target.suffix
            counter = 1
            while True:
                candidate = dest_dir / f"{stem}_{counter}{suffix}"
                if not candidate.exists():
                    return candidate
                counter += 1

    def run(self):
        while self._running:
            try:
                task = self._queue.get(timeout=0.2)
            except queue.Empty:
                if self._running:
                    continue
                else:
                    break

            if task is None:
                break

            try:
                self._process_task(task)
            except Exception as e:
                self.task_failed.emit({
                    "action_type": task.action_type,
                    "source_path": task.source_path,
                    "image_index": task.image_index,
                    "error": str(e)
                })
            finally:
                self._queue.task_done()
                if self._queue.empty():
                    self.queue_empty.emit()

    def _process_task(self, task: FileActionTask):
        source_p = Path(task.source_path)
        dest_dir = Path(task.target_dir)

        # 1. Handling Revert / Undo Operations
        if task.action_type == "revert_move":
            # Move back from target to source
            if not source_p.exists():
                raise FileNotFoundError(f"File target tidak ditemukan untuk di-undo: {source_p}")
            dest_dir.mkdir(parents=True, exist_ok=True)
            reverted_path = dest_dir / source_p.name
            if task.explicit_target_path:
                reverted_path = Path(task.explicit_target_path)
            shutil.move(str(source_p), str(reverted_path))
            self.task_completed.emit({
                "action_type": "revert_move",
                "source_path": str(source_p),
                "target_path": str(reverted_path),
                "image_index": task.image_index,
                "status": "reverted"
            })
            return

        elif task.action_type == "revert_copy":
            # Delete copied target file
            target_to_remove = Path(task.explicit_target_path or task.source_path)
            if target_to_remove.exists():
                os.remove(str(target_to_remove))
            self.task_completed.emit({
                "action_type": "revert_copy",
                "source_path": str(target_to_remove),
                "target_path": None,
                "image_index": task.image_index,
                "status": "reverted"
            })
            return

        # 2. Standard Move or Copy Operations
        if not source_p.exists():
            raise FileNotFoundError(f"File asal tidak ditemukan: {source_p}")

        dest_dir.mkdir(parents=True, exist_ok=True)

        if task.explicit_target_path:
            target_p = Path(task.explicit_target_path)
        else:
            target_p = self.resolve_target_collision(dest_dir, source_p.name, task.duplicate_strategy)

        if target_p is None:
            # Skipped due to collision
            self.task_completed.emit({
                "action_type": task.action_type,
                "source_path": str(source_p),
                "target_path": None,
                "image_index": task.image_index,
                "status": "skipped_collision"
            })
            return

        if task.action_type == "move":
            shutil.move(str(source_p), str(target_p))
        elif task.action_type == "copy":
            shutil.copy2(str(source_p), str(target_p))
        else:
            raise ValueError(f"Tipe aksi tidak dikenal: {task.action_type}")

        self.task_completed.emit({
            "action_type": task.action_type,
            "source_path": str(source_p),
            "target_path": str(target_p),
            "image_index": task.image_index,
            "status": "success"
        })
