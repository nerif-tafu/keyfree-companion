@echo off
echo Starting KeyFree Companion...
echo.
echo This will launch both the GUI and server silently.
echo The application will be available at: http://localhost:3000
echo.
echo The GUI will open automatically - no terminal window needed.
echo.

REM Check if executable exists
if not exist "dist\KeyFreeCompanion.exe" (
    echo Error: KeyFreeCompanion.exe not found in dist folder!
    echo Please build the application first using: pyinstaller --clean keyfree_companion.spec
    pause
    exit /b 1
)

REM Launch the application
start "" "dist\KeyFreeCompanion.exe" start

echo KeyFree Companion started successfully!
echo GUI should open automatically.
echo.
echo To test the API, open a new terminal and run:
echo curl.exe http://localhost:3000/health
echo.
pause
