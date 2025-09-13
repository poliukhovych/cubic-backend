@echo off
echo Starting Cubic Backend API Server...
echo.

REM Try different Python commands
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo Using python command...
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    goto :end
)

where py >nul 2>&1
if %errorlevel% equ 0 (
    echo Using py launcher...
    py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    goto :end
)

where python3 >nul 2>&1
if %errorlevel% equ 0 (
    echo Using python3 command...
    python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    goto :end
)

echo.
echo Error: Python is not installed or not found in PATH
echo Please install Python 3.8+ and add it to your PATH
echo.

:end
pause
