@echo off
echo ========================================
echo ERCU ABI TELEGRAM COMMANDER - EXE BUILDER
echo ========================================
echo.

REM Gerekli paketleri kur
echo [1/3] Gerekli paketler kuruluyor...
pip install --upgrade pip
pip install pyrogram customtkinter tgcrypto pyinstaller

echo.
echo [2/3] EXE dosyasi olusturuluyor...
pyinstaller --noconfirm --onefile --windowed ^
    --name="ErcuCommander" ^
    --add-data="accounts.json;." ^
    --add-data="sablonlar.json;." ^
    --add-data="gonderilenler.txt;." ^
    --hidden-import=pyrogram ^
    --hidden-import=customtkinter ^
    telegram_commander_fixed.py

echo.
echo [3/3] Temizlik yapiliyor...
rmdir /s /q build
del ErcuCommander.spec

echo.
echo ========================================
echo TAMAMLANDI!
echo EXE dosyasi: dist\ErcuCommander.exe
echo ========================================
pause
