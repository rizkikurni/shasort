import os
from pathlib import Path
from typing import Dict, Any
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView
)

class SummaryDialog(QDialog):
    """
    Summary dialog displayed when sorting is finished or when user finishes.
    Shows detailed stats of photos sorted by folder without emojis or glow.
    """
    def __init__(self, parent=None, summary_stats: Dict[str, Any] = None, 
                 dest_root: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Sesi Sortir Selesai")
        self.setFixedSize(480, 440)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.summary_stats = summary_stats or {"total_processed": 0, "skipped": 0, "by_subfolder": {}}
        self.dest_root = dest_root

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)

        # Header Title
        title = QLabel("RINGKASAN SESI SORTIR", self)
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        total = self.summary_stats.get("total_processed", 0)
        skipped = self.summary_stats.get("skipped", 0)
        moved_or_copied = total - skipped

        subtitle = QLabel(f"Sebanyak <b>{total}</b> foto telah ditinjau ({moved_or_copied} dipindah/disalin, {skipped} dilewati).", self)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #a1a1aa; font-size: 12px;")
        layout.addWidget(subtitle)

        # Stats Breakdown Table
        table_lbl = QLabel("DISTRIBUSI SUBFOLDER TUJUAN", self)
        table_lbl.setObjectName("sectionHeader")
        layout.addWidget(table_lbl)

        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Nama Subfolder", "Jumlah Foto"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        by_subfolder = self.summary_stats.get("by_subfolder", {})
        self.table.setRowCount(len(by_subfolder) + (1 if skipped > 0 else 0))

        row_idx = 0
        for folder, count in sorted(by_subfolder.items()):
            folder_item = QTableWidgetItem(folder)
            count_item = QTableWidgetItem(f"{count} foto")
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, folder_item)
            self.table.setItem(row_idx, 1, count_item)
            row_idx += 1

        if skipped > 0:
            skip_item = QTableWidgetItem("(Dilewati / Tanpa Aksi)")
            skip_item.setForeground(Qt.GlobalColor.gray)
            skip_count_item = QTableWidgetItem(f"{skipped} foto")
            skip_count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            skip_count_item.setForeground(Qt.GlobalColor.gray)
            self.table.setItem(row_idx, 0, skip_item)
            self.table.setItem(row_idx, 1, skip_count_item)

        layout.addWidget(self.table)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        if self.dest_root and os.path.isdir(self.dest_root):
            self.open_folder_btn = QPushButton("Buka Folder Hasil", self)
            self.open_folder_btn.clicked.connect(self._open_dest_folder)
            btn_layout.addWidget(self.open_folder_btn)

        self.setup_btn = QPushButton("Kembali ke Setup", self)
        self.setup_btn.setObjectName("startBtn")
        self.setup_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.setup_btn)

        layout.addLayout(btn_layout)

    def _open_dest_folder(self):
        if self.dest_root and os.path.isdir(self.dest_root):
            try:
                os.startfile(self.dest_root)
            except Exception as e:
                print(f"Gagal membuka folder: {e}")
