@echo off
echo Cleaning up old builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "Combine_pdf_tool.spec" del /f /q "Combine_pdf_tool.spec"

echo Installing requirements...
pip install -r requirements.txt

echo Building standalone executable...
python -m PyInstaller --noconfirm --onedir --windowed --name "Combine_pdf_tool" --clean main.py

echo.
echo ====================================================
echo Build finished!
echo Your executable is in the 'dist\Combine_pdf_tool' folder.
echo You can zip this folder and send it to others.
echo ====================================================
pause
