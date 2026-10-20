@echo off
REM Сборка File Organizer в один .exe
pip install -r requirements-dev.txt
pyinstaller --noconfirm --clean --onefile --windowed --name "FileOrganizer" --collect-all customtkinter main.py
echo.
echo Готово! Файл: dist\FileOrganizer.exe
pause
