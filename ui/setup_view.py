import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QRadioButton, QButtonGroup, QComboBox, 
    QTableWidget, QHeaderView, QFileDialog, 
    QMessageBox, QInputDialog, QGroupBox, QFrame
)

from core.config_manager import ConfigManager
from core.image_loader import ImageLoader
from ui.widgets.key_input_dialog import KeyInputDialog

class SetupView(QWidget):
    """
    Setup & Configuration View.
    Configures source/destination paths, operation mode, presets, and keybinding table.
    Designed with a clean, professional aesthetic without AI slop/emojis.
    """
    start_sorting = pyqtSignal(dict)  # Emits payload when user starts sorting

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("setupView")
        self._init_ui()
        self._load_initial_state()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 22, 28, 22)
        main_layout.setSpacing(14)

        # 1. Header Bar
        header_layout = QHBoxLayout()
        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(2)

        title = QLabel("SHASORT", self)
        title.setObjectName("titleLabel")
        subtitle = QLabel("Shashin (Foto) + Sort — Sortir foto cepat, minim fatigue, dan bebas salah pencet.", self)
        subtitle.setObjectName("subtitleLabel")

        header_text_layout.addWidget(title)
        header_text_layout.addWidget(subtitle)
        header_layout.addLayout(header_text_layout)
        header_layout.addStretch()

        # Preset Selector Controls in Header
        preset_box = QHBoxLayout()
        preset_box.setSpacing(8)
        preset_lbl = QLabel("Preset:", self)
        preset_lbl.setStyleSheet("color: #8e8e93; font-weight: 500;")
        
        self.preset_combo = QComboBox(self)
        self.preset_combo.setMinimumWidth(180)
        self.preset_combo.currentIndexChanged.connect(self._on_preset_selected)

        self.save_preset_btn = QPushButton("Simpan Preset", self)
        self.save_preset_btn.setObjectName("secondaryBtn")
        self.save_preset_btn.clicked.connect(self._save_custom_preset)

        self.import_preset_btn = QPushButton("Muat JSON...", self)
        self.import_preset_btn.setObjectName("secondaryBtn")
        self.import_preset_btn.clicked.connect(self._import_preset_file)

        preset_box.addWidget(preset_lbl)
        preset_box.addWidget(self.preset_combo)
        preset_box.addWidget(self.save_preset_btn)
        preset_box.addWidget(self.import_preset_btn)
        header_layout.addLayout(preset_box)

        main_layout.addLayout(header_layout)

        # 2. Directory Configuration Card
        folder_group = QGroupBox("DIREKTORI FOTO", self)
        folder_layout = QVBoxLayout(folder_group)
        folder_layout.setSpacing(10)

        # Source folder row
        src_row = QHBoxLayout()
        src_row.setSpacing(8)
        src_lbl = QLabel("Folder Sumber:", self)
        src_lbl.setFixedWidth(105)
        self.src_input = QLineEdit(self)
        self.src_input.setPlaceholderText("Pilih direktori foto asal...")
        self.src_input.textChanged.connect(self._check_source_photos)
        
        self.src_browse_btn = QPushButton("Pilih...", self)
        self.src_browse_btn.setObjectName("browseBtn")
        self.src_browse_btn.clicked.connect(self._browse_source)

        self.src_info_lbl = QLabel("", self)
        self.src_info_lbl.setMinimumWidth(110)
        self.src_info_lbl.setStyleSheet("color: #60a5fa; font-weight: 500; font-size: 11px;")

        src_row.addWidget(src_lbl)
        src_row.addWidget(self.src_input, stretch=1)
        src_row.addWidget(self.src_browse_btn)
        src_row.addWidget(self.src_info_lbl)
        folder_layout.addLayout(src_row)

        # Destination folder row
        dest_row = QHBoxLayout()
        dest_row.setSpacing(8)
        dest_lbl = QLabel("Folder Tujuan:", self)
        dest_lbl.setFixedWidth(105)
        self.dest_input = QLineEdit(self)
        self.dest_input.setPlaceholderText("Pilih direktori induk untuk subfolder hasil sortir...")
        
        self.dest_browse_btn = QPushButton("Pilih...", self)
        self.dest_browse_btn.setObjectName("browseBtn")
        self.dest_browse_btn.clicked.connect(self._browse_destination)

        dest_placeholder = QLabel("", self)
        dest_placeholder.setMinimumWidth(110)

        dest_row.addWidget(dest_lbl)
        dest_row.addWidget(self.dest_input, stretch=1)
        dest_row.addWidget(self.dest_browse_btn)
        dest_row.addWidget(dest_placeholder)
        folder_layout.addLayout(dest_row)

        # Mode and Collision Options
        options_row = QHBoxLayout()
        options_row.setSpacing(20)

        mode_lbl = QLabel("Mode Operasi:", self)
        mode_lbl.setFixedWidth(105)
        options_row.addWidget(mode_lbl)

        self.mode_group = QButtonGroup(self)
        self.move_radio = QRadioButton("Pindah Langsung (Cut / Move)", self)
        self.copy_radio = QRadioButton("Salin (Copy - Tetap Simpan Asli)", self)
        self.move_radio.setChecked(True)
        self.mode_group.addButton(self.move_radio)
        self.mode_group.addButton(self.copy_radio)

        options_row.addWidget(self.move_radio)
        options_row.addWidget(self.copy_radio)
        options_row.addSpacing(20)

        collision_lbl = QLabel("Nama Kembar:", self)
        self.collision_combo = QComboBox(self)
        self.collision_combo.addItems([
            "Rename Otomatis (_1, _2)",
            "Lewati (Skip)",
            "Timpa (Overwrite)"
        ])
        options_row.addWidget(collision_lbl)
        options_row.addWidget(self.collision_combo)
        options_row.addStretch()

        folder_layout.addLayout(options_row)
        main_layout.addWidget(folder_group)

        # 3. Keybinding & Subfolder Mapping Table
        table_group = QGroupBox("MAPPING TOMBOL & SUBFOLDER", self)
        table_layout = QVBoxLayout(table_group)
        table_layout.setSpacing(8)

        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Tombol", "Nama Subfolder", "Keterangan (Opsional)", "Aksi"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 90)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 70)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table_layout.addWidget(self.table)

        table_btn_row = QHBoxLayout()
        self.add_row_btn = QPushButton("+ Tambah Shortcut", self)
        self.add_row_btn.clicked.connect(self._add_shortcut_row)

        hint_lbl = QLabel("Tip: Klik tombol pada kolom 'Tombol' untuk merekam shortcut keyboard baru.", self)
        hint_lbl.setStyleSheet("color: #71717a; font-size: 11px;")

        table_btn_row.addWidget(self.add_row_btn)
        table_btn_row.addSpacing(10)
        table_btn_row.addWidget(hint_lbl)
        table_btn_row.addStretch()
        table_layout.addLayout(table_btn_row)

        main_layout.addWidget(table_group)

        # 4. Action Footer
        footer_layout = QHBoxLayout()
        self.status_lbl = QLabel("", self)
        self.status_lbl.setStyleSheet("color: #ef4444; font-weight: 500;")

        self.start_btn = QPushButton("MULAI SORTIR (F5)", self)
        self.start_btn.setObjectName("startBtn")
        self.start_btn.setMinimumHeight(38)
        self.start_btn.setMinimumWidth(180)
        self.start_btn.clicked.connect(self._validate_and_start)

        footer_layout.addWidget(self.status_lbl)
        footer_layout.addStretch()
        footer_layout.addWidget(self.start_btn)
        main_layout.addLayout(footer_layout)

    def _load_initial_state(self):
        """Loads user settings and presets on startup."""
        self._refresh_presets_dropdown()

        settings = ConfigManager.load_user_settings()
        if settings.get("last_source"):
            self.src_input.setText(settings["last_source"])
            self._check_source_photos(settings["last_source"])
        if settings.get("last_destination"):
            self.dest_input.setText(settings["last_destination"])

        if settings.get("mode") == "copy":
            self.copy_radio.setChecked(True)
        else:
            self.move_radio.setChecked(True)

        strat_map = {"rename": 0, "skip": 1, "overwrite": 2}
        idx = strat_map.get(settings.get("duplicate_strategy", "rename"), 0)
        self.collision_combo.setCurrentIndex(idx)

        # Explicitly load preset data on initial startup
        last_preset = settings.get("last_preset", "Wedding Sorter")
        found_idx = self.preset_combo.findText(last_preset)
        if found_idx >= 0:
            self.preset_combo.setCurrentIndex(found_idx)
            file_stem = self.preset_combo.itemData(found_idx)
            preset_data = ConfigManager.load_preset(file_stem or "wedding")
        else:
            preset_data = ConfigManager.load_preset("wedding")

        self._load_preset_data(preset_data)

    def _refresh_presets_dropdown(self):
        current_text = self.preset_combo.currentText()
        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()

        presets = ConfigManager.list_presets()
        for p in presets:
            self.preset_combo.addItem(p["profile_name"], p["file_stem"])

        if current_text:
            idx = self.preset_combo.findText(current_text)
            if idx >= 0:
                self.preset_combo.setCurrentIndex(idx)

        self.preset_combo.blockSignals(False)

    def _on_preset_selected(self, index: int):
        if index < 0:
            return
        file_stem = self.preset_combo.itemData(index)
        preset_data = ConfigManager.load_preset(file_stem)
        self._load_preset_data(preset_data)

    def _load_preset_data(self, data: Dict[str, Any]):
        """Populates form and table from loaded preset dictionary."""
        mode = data.get("mode", "move")
        if mode == "copy":
            self.copy_radio.setChecked(True)
        else:
            self.move_radio.setChecked(True)

        strategy = data.get("duplicate_strategy", "rename")
        strat_map = {"rename": 0, "skip": 1, "overwrite": 2}
        self.collision_combo.setCurrentIndex(strat_map.get(strategy, 0))

        # Clear and repopulate table with interactive row widgets
        bindings = data.get("bindings", {})
        self.table.setRowCount(0)
        for key, info in bindings.items():
            self._add_row_item(str(key), info.get("folder", ""), info.get("label", ""))

    def _add_row_item(self, key: str, folder: str, label: str):
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        self.table.setRowHeight(row_idx, 36)

        # Col 0: Key Selection Button
        key_btn = QPushButton(key, self)
        key_btn.setObjectName("keySelectBtn")
        key_btn.setToolTip("Klik untuk mengubah tombol shortcut ini")
        key_btn.clicked.connect(lambda _, b=key_btn: self._reassign_key(b))
        self.table.setCellWidget(row_idx, 0, key_btn)

        # Col 1: Subfolder Name Input (direct QLineEdit for 100% reliable editing)
        folder_edit = QLineEdit(folder, self)
        folder_edit.setPlaceholderText("Nama subfolder...")
        self.table.setCellWidget(row_idx, 1, folder_edit)

        # Col 2: Description Input
        label_edit = QLineEdit(label, self)
        label_edit.setPlaceholderText("Keterangan...")
        self.table.setCellWidget(row_idx, 2, label_edit)

        # Col 3: Delete Button
        del_btn = QPushButton("Hapus", self)
        del_btn.setObjectName("dangerBtn")
        del_btn.setFixedSize(54, 26)
        del_btn.clicked.connect(lambda _, b=del_btn: self._delete_row_by_button(b))
        self.table.setCellWidget(row_idx, 3, del_btn)

    def _reassign_key(self, button: QPushButton):
        """Opens key input dialog to change button's assigned shortcut."""
        current_key = button.text()
        new_key, ok = KeyInputDialog.get_key(self, current_key)
        if ok and new_key:
            button.setText(new_key)

    def _delete_row_by_button(self, button: QPushButton):
        for r in range(self.table.rowCount()):
            if self.table.cellWidget(r, 3) == button:
                self.table.removeRow(r)
                return

    def _add_shortcut_row(self):
        key, ok = KeyInputDialog.get_key(self)
        if ok and key:
            self._add_row_item(key, f"Folder_{key}", "")

    def _browse_source(self):
        curr = self.src_input.text() or os.path.expanduser("~")
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Sumber Foto", curr)
        if folder:
            self.src_input.setText(folder)
            self._check_source_photos(folder)

    def _browse_destination(self):
        curr = self.dest_input.text() or os.path.expanduser("~")
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Tujuan Utama", curr)
        if folder:
            self.dest_input.setText(folder)

    def _check_source_photos(self, path: str):
        if not path or not os.path.isdir(path):
            self.src_info_lbl.setText("")
            return

        count = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file() and ImageLoader.is_supported(entry.path):
                    count += 1
            self.src_info_lbl.setText(f"({count} foto)")
        except Exception:
            self.src_info_lbl.setText("")

    def _get_current_bindings(self) -> Dict[str, Any]:
        bindings = {}
        for r in range(self.table.rowCount()):
            key_btn = self.table.cellWidget(r, 0)
            folder_edit = self.table.cellWidget(r, 1)
            label_edit = self.table.cellWidget(r, 2)

            if isinstance(key_btn, QPushButton) and isinstance(folder_edit, QLineEdit):
                k = key_btn.text().strip()
                folder = ConfigManager.sanitize_folder_name(folder_edit.text())
                lbl = label_edit.text().strip() if isinstance(label_edit, QLineEdit) else ""
                if k and folder:
                    bindings[k] = {"folder": folder, "label": lbl}
        return bindings

    def _save_custom_preset(self):
        bindings = self._get_current_bindings()
        if not bindings:
            QMessageBox.warning(self, "Preset Kosong", "Tabel shortcut belum memiliki tombol yang diatur.")
            return

        name, ok = QInputDialog.getText(self, "Simpan Preset", "Masukkan nama preset baru:")
        if ok and name.strip():
            strat_list = ["rename", "skip", "overwrite"]
            config_data = {
                "profile_name": name.strip(),
                "mode": "move" if self.move_radio.isChecked() else "copy",
                "duplicate_strategy": strat_list[self.collision_combo.currentIndex()],
                "bindings": bindings
            }
            ConfigManager.save_preset(name.strip(), config_data)
            self._refresh_presets_dropdown()
            idx = self.preset_combo.findText(name.strip())
            if idx >= 0:
                self.preset_combo.setCurrentIndex(idx)
            QMessageBox.information(self, "Preset Tersimpan", f"Preset '{name.strip()}' berhasil disimpan.")

    def _import_preset_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih File Preset JSON", "", "JSON Files (*.json)")
        if file_path:
            data = ConfigManager.load_preset(file_path)
            self._load_preset_data(data)
            self._refresh_presets_dropdown()

    def _validate_and_start(self):
        src = self.src_input.text().strip()
        dest = self.dest_input.text().strip()

        if not src or not os.path.isdir(src):
            self.status_lbl.setText("Folder sumber tidak valid atau belum dipilih!")
            return

        if not dest:
            self.status_lbl.setText("Folder tujuan belum dipilih!")
            return

        if os.path.abspath(src) == os.path.abspath(dest):
            self.status_lbl.setText("Folder sumber dan tujuan tidak boleh sama!")
            return

        bindings = self._get_current_bindings()
        if not bindings:
            self.status_lbl.setText("Minimal harus ada 1 shortcut tombol yang dikonfigurasi!")
            return

        # Scan for images in source folder
        image_files = []
        try:
            for entry in os.scandir(src):
                if entry.is_file() and ImageLoader.is_supported(entry.path):
                    image_files.append(entry.path)
            image_files.sort()
        except Exception as e:
            self.status_lbl.setText(f"Gagal membaca folder sumber: {e}")
            return

        if not image_files:
            self.status_lbl.setText("Tidak ada file foto yang didukung di folder sumber!")
            return

        self.status_lbl.setText("")

        strat_list = ["rename", "skip", "overwrite"]
        strategy = strat_list[self.collision_combo.currentIndex()]
        mode = "move" if self.move_radio.isChecked() else "copy"

        # Save user preferences for next session
        ConfigManager.save_user_settings({
            "last_source": src,
            "last_destination": dest,
            "last_preset": self.preset_combo.currentText(),
            "mode": mode,
            "duplicate_strategy": strategy
        })

        session_config = {
            "source_dir": src,
            "dest_root": dest,
            "mode": mode,
            "duplicate_strategy": strategy,
            "bindings": bindings,
            "image_files": image_files
        }

        self.start_sorting.emit(session_config)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F5:
            self._validate_and_start()
        else:
            super().keyPressEvent(event)
