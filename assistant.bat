@echo off
setlocal

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Python is not installed or not in your PATH.
    echo J.A.R.V.I.S. requires Python to bootstrap.
    echo.
    echo Please install Python 3.13 from https://www.python.org/downloads/
    echo and ensure "Add Python to PATH" is checked during installation.
    echo.
    pause
    exit /b 1
)

:: Pass arguments to the python bootstrapper
python "%~dp0cli\bootstrap.py" %*

endlocal
