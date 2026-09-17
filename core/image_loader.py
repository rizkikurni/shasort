import os
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Any, Optional, List
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QMutex, QMutexLocker
from PyQt6.QtGui import QImage, QPixmap, QImageReader
from PIL import Image, ImageOps

SUPPORTED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", 
    ".jfif", ".cr2", ".nef", ".arw", ".dng"
}

class ImageData:
    """Holds decoded image data and metadata."""
    def __init__(self, path: str, pixmap: Optional[QPixmap], 
                 width: int, height: int, filesize_bytes: int, 
                 error: Optional[str] = None):
        self.path = path
        self.pixmap = pixmap
        self.width = width
        self.height = height
        self.filesize_bytes = filesize_bytes
        self.error = error

    @property
    def megapixels(self) -> float:
        if self.width > 0 and self.height > 0:
            return round((self.width * self.height) / 1_000_000, 1)
        return 0.0

    @property
    def filesize_mb(self) -> float:
        return round(self.filesize_bytes / (1024 * 1024), 2)

    @property
    def filename(self) -> str:
        return Path(self.path).name


class ImageLoaderWorker(QThread):
    """Background thread to preload images into memory without blocking UI."""
    image_ready = pyqtSignal(str, object)  # emits (path, ImageData)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._request_queue: List[str] = []
        self._mutex = QMutex()
        self._running = True

    def queue_paths(self, paths: List[str]):
        with QMutexLocker(self._mutex):
            # Prioritize newest requests while avoiding duplicate redundant work
            self._request_queue = [p for p in paths if os.path.isfile(p)]

    def stop(self):
        self._running = False
        self.wait(1500)

    def run(self):
        while self._running:
            target_path = None
            with QMutexLocker(self._mutex):
                if self._request_queue:
                    target_path = self._request_queue.pop(0)

            if target_path is None:
                self.msleep(30)
                continue

            # Load image
            img_data = ImageLoader.load_image_from_disk(target_path)
            self.image_ready.emit(target_path, img_data)


class ImageLoader(QObject):
    """
    High-performance image cache and preloader with EXIF rotation support.
    Maintains an LRU cache of decoded images for 0ms transitions.
    """
    image_preloaded = pyqtSignal(str)  # emitted when an image finishes background loading

    def __init__(self, max_cache_size: int = 16, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.max_cache_size = max_cache_size
        self._cache: OrderedDict[str, ImageData] = OrderedDict()
        self._mutex = QMutex()

        self._worker = ImageLoaderWorker()
        self._worker.image_ready.connect(self._on_worker_image_ready)
        self._worker.start()

    def stop(self):
        """Stops background preloader thread."""
        self._worker.stop()

    @staticmethod
    def is_supported(file_path: str) -> bool:
        """Checks if file extension is a supported image format."""
        return Path(file_path).suffix.lower() in SUPPORTED_EXTENSIONS

    @staticmethod
    def load_image_from_disk(path: str) -> ImageData:
        """
        Loads an image from disk with automatic EXIF orientation.
        Tries QImageReader first for speed, falls back to Pillow if needed.
        """
        if not os.path.isfile(path):
            return ImageData(path, None, 0, 0, 0, error="File tidak ditemukan")

        filesize = os.path.getsize(path)

        # 1. Try QImageReader with auto-transform
        reader = QImageReader(path)
        reader.setAutoTransform(True)
        qimg = reader.read()

        if not qimg.isNull():
            pixmap = QPixmap.fromImage(qimg)
            return ImageData(
                path=path,
                pixmap=pixmap,
                width=qimg.width(),
                height=qimg.height(),
                filesize_bytes=filesize
            )

        # 2. Fallback to Pillow with EXIF transpose
        try:
            with Image.open(path) as pil_img:
                pil_img = ImageOps.exif_transpose(pil_img)
                # Convert to RGB or RGBA for Qt compatibility
                if pil_img.mode not in ("RGB", "RGBA"):
                    pil_img = pil_img.convert("RGB")
                
                width, height = pil_img.size
                data = pil_img.tobytes("raw", pil_img.mode)
                fmt = QImage.Format.Format_RGBA8888 if pil_img.mode == "RGBA" else QImage.Format.Format_RGB888
                bytes_per_line = 4 * width if pil_img.mode == "RGBA" else 3 * width
                qimg = QImage(data, width, height, bytes_per_line, fmt)
                pixmap = QPixmap.fromImage(qimg)
                return ImageData(
                    path=path,
                    pixmap=pixmap,
                    width=width,
                    height=height,
                    filesize_bytes=filesize
                )
        except Exception as e:
            return ImageData(path, None, 0, 0, filesize, error=f"Gagal memuat gambar: {e}")

    def get_image(self, path: str) -> ImageData:
        """
        Retrieves image from memory cache if present;
        otherwise synchronously loads from disk and updates cache.
        """
        with QMutexLocker(self._mutex):
            if path in self._cache:
                self._cache.move_to_end(path)
                return self._cache[path]

        # Not in cache: load immediately
        data = self.load_image_from_disk(path)
        self._add_to_cache(path, data)
        return data

    def preload(self, paths: List[str]):
        """Queues paths to be preloaded into memory by worker thread."""
        needed_paths = []
        with QMutexLocker(self._mutex):
            for p in paths:
                if p and p not in self._cache:
                    needed_paths.append(p)

        if needed_paths:
            self._worker.queue_paths(needed_paths)

    def evict(self, path: str):
        """Removes a specific path from cache (e.g. after move/delete)."""
        with QMutexLocker(self._mutex):
            if path in self._cache:
                del self._cache[path]

    def clear(self):
        """Clears all cached images."""
        with QMutexLocker(self._mutex):
            self._cache.clear()

    def _add_to_cache(self, path: str, data: ImageData):
        with QMutexLocker(self._mutex):
            self._cache[path] = data
            self._cache.move_to_end(path)
            while len(self._cache) > self.max_cache_size:
                self._cache.popitem(last=False)

    def _on_worker_image_ready(self, path: str, img_data: ImageData):
        self._add_to_cache(path, img_data)
        self.image_preloaded.emit(path)
