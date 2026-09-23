@echo off
title ShaSort - Build Single Portable EXE
echo ========================================================
echo  MENGOMPILASI SHASORT MENJADI APLIKASI PC (.EXE)
echo ========================================================
echo Proses ini membutuhkan waktu sekitar 30 - 60 detik...
echo Mohon tunggu hingga selesai...
echo.

python -m PyInstaller --noconsole --onefile --name "ShaSort" --add-data "presets;presets" --clean -y main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo  BUILD BERHASIL!
    echo ========================================================
    echo Menyalin ShaSort.exe ke folder utama ini...
    copy /Y "dist\ShaSort.exe" ".\ShaSort.exe" >nul
    echo.
    echo Aplikasi portable siap digunakan:
    echo --^> %~dp0ShaSort.exe
    echo.
    echo Membuka folder dan memilih ShaSort.exe...
    explorer.exe /select,"%~dp0ShaSort.exe"
) else (
    echo.
    echo [ERROR] Build Gagal! Silakan periksa pesan error di atas.
)

echo.
pause
