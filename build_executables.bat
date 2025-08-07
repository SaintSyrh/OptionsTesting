@echo off
echo ============================================================
echo     BUILDING WINDOWS EXECUTABLES
echo ============================================================
echo.

echo Installing PyInstaller if needed...
pip install pyinstaller

echo.
echo Building installer.exe...
pyinstaller --onefile --console --name=installer --clean installer.py

echo.
echo Building launcher.exe...
pyinstaller --onefile --console --name=launcher --clean launcher.py

echo.
echo Moving executables to main directory...
if exist "dist\installer.exe" move "dist\installer.exe" "installer.exe"
if exist "dist\launcher.exe" move "dist\launcher.exe" "launcher.exe"

echo.
echo Cleaning up build files...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "installer.spec" del "installer.spec"
if exist "launcher.spec" del "launcher.spec"

echo.
echo ============================================================
echo     BUILD COMPLETE!
echo ============================================================
echo.
echo Created files:
echo - installer.exe (run this first for setup)
echo - launcher.exe (run this to start the app)
echo.
echo To distribute, include these files:
echo - installer.exe
echo - launcher.exe  
echo - streamlit_app.py
echo - option_pricing.py
echo - requirements.txt
echo ============================================================
echo.
pause