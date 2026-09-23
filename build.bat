@echo off
title ShaSort - Build Folder Bundle
echo ========================================================
echo  MENGOMPILASI SHASORT (FOLDER BUNDLE - FAST STARTUP)
echo ========================================================
echo Proses ini membutuhkan waktu sekitar 20 - 40 detik...
echo Mohon tunggu hingga selesai...
echo.

python -m PyInstaller --noconsole --onedir --name "ShaSort" --add-data "presets;presets" --clean -y main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo  BUILD BERHASIL!
    echo ========================================================
    echo Aplikasi siap digunakan di:
    echo --^> %~dp0dist\ShaSort\ShaSort.exe
    echo.
    echo Membuka folder hasil build...
    explorer.exe /select,"%~dp0dist\ShaSort\ShaSort.exe"
) else (
    echo.
    echo [ERROR] Build Gagal! Silakan periksa pesan error di atas.
)

echo.
pause
