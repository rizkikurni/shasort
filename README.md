# ShaSort

Aplikasi sortir foto desktop berkecepatan tinggi berbasis **PyQt6** yang dirancang untuk meminimalkan kelelahan mata (*fatigue*), mencegah salah pencet, dan menangani foto resolusi tinggi (10–30+ MB) dengan **latensi 0ms**.

> Nama **ShaSort** terinspirasi dari kata bahasa Jepang **shashin** (写真 - foto) dan **sort** (sortir).

---

## Fitur Utama

* **Dual-State Screen:**
  - **Setup View:** Pilih folder sumber foto, folder tujuan hasil sortir, mode operasi (*Cut/Move* vs *Copy*), strategi penanganan nama file kembar (*Auto-rename*, *Skip*, *Overwrite*), serta konfigurasi shortcut keyboard.
  - **Action View (Focus Mode):** Viewer layar penuh minimalis berlatar belakang gelap (`#18181b`) untuk menjaga akurasi warna dan kenyamanan mata saat menyortir ratusan/ribuan foto, dilengkapi **HUD overlay transparan** di bagian bawah.
* **Fitur Safety (Undo / Revert History):**
  - Salah pencet tombol? Tekan `Ctrl + Z` atau `Backspace` untuk secara instan membatalkan pemindahan/penyalinan dan memulihkan foto ke posisi semula.
* **Preloading RAM & Async Disk I/O:**
  - Pemindahan/penyalinan file dijalankan pada background thread (`FileWorker`), sehingga antarmuka tidak akan pernah *freeze* meskipun memproses file RAW/JPEG ukuran besar.
  - Preloader otomatis memuat 1–2 foto ke depan ke dalam RAM dan menangani orientasi EXIF kamera secara otomatis.
* **Collision Handler (Nama File Kembar):**
  - Mencegah file tertimpa secara tidak sengaja dengan menambahkan suffix nomor secara otomatis (`foto_1.jpg`, `foto_2.jpg`).
* **Preset Profiles:**
  - Dilengkapi preset bawaan:
    - `Wedding Sorter` (Close-Up, Foto Bareng, Dokumentasi, Dekorasi, Sampah/Blur)
    - `Liburan & Traveling` (Pemandangan, Kuliner, Orang/Potret, Hotel/Transport, Sampah)
    - `Street Photography` (Candid, Arsitektur, Portrait, B&W Candidate, Ditolak)
  - Pengguna dapat menyimpan dan memuat preset kustom ke format JSON.

---

## Panduan Pintasan Keyboard (Shortcut Keys)

| Tombol | Aksi |
| :--- | :--- |
| **`1` .. `9` / Huruf kustom** | Pindah / Salin foto ke subfolder yang dikonfigurasi |
| **`Space`** | Lewati foto saat ini tanpa memindah (*Skip*) |
| **`Ctrl + Z`** / **`Backspace`** | Batalkan aksi terakhir (*Undo*) & pulihkan foto |
| **`A`** / **`Panah Kiri`** | Tinjau foto sebelumnya (*Previous*) |
| **`D`** / **`Panah Kanan`** | Tinjau foto selanjutnya (*Next*) |
| **`Esc`** | Keluar dari Focus View & kembali ke menu Setup |
| **`F5`** | Mulai sortir dari layar Setup View |

---

## Cara Menjalankan

1. Pastikan dependensi terpasang:
   ```bash
   pip install PyQt6 pillow
   ```
2. Jalankan aplikasi:
   ```bash
   python main.py
   ```
3. Menjalankan pengujian otomatis (Unit & Integration Tests):
   ```bash
   python tests/test_sorter.py
   python tests/test_ui_flow.py
   ```
