@echo off
:: ============================================================
::  Smart Business Idea Generator — Python Setup & Run Script
::  Automatically installs Python if missing, then runs the app
:: ============================================================
title Smart Business Idea Generator Setup

echo.
echo  ============================================================
echo   Smart Business Idea Generator
echo   Powered by IBM Granite AI
echo  ============================================================
echo.

:: ── Step 1: Detect any working Python ───────────────────────
set PYTHON_EXE=

:: Check common install paths
for %%P in (
  "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
  "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
  "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
  "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
  "%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
  "C:\Python313\python.exe"
  "C:\Python312\python.exe"
  "C:\Python311\python.exe"
  "C:\Python310\python.exe"
  "C:\Python39\python.exe"
  "%USERPROFILE%\AppData\Local\Programs\Python\Python313\python.exe"
  "%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe"
  "C:\ProgramData\Anaconda3\python.exe"
  "C:\Anaconda3\python.exe"
  "%USERPROFILE%\Anaconda3\python.exe"
  "%USERPROFILE%\miniconda3\python.exe"
  "C:\miniconda3\python.exe"
) do (
  if exist %%P (
    set PYTHON_EXE=%%P
    goto :found_python
  )
)

:: ── Step 2: Python not found — download installer ───────────
echo  [!] Python not found on this system.
echo  [*] Downloading Python 3.12 installer from python.org...
echo.

set INSTALLER=%TEMP%\python-3.12.7-installer.exe
set DOWNLOAD_URL=https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe

:: Use PowerShell to download
powershell -NoProfile -Command "& { [Net.ServicePointManager]::SecurityProtocol = 'Tls12'; Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%INSTALLER%' -UseBasicParsing }"

if not exist "%INSTALLER%" (
  echo.
  echo  [ERROR] Download failed. Please install Python manually:
  echo          https://www.python.org/downloads/
  echo.
  echo  During installation, check "Add Python to PATH" checkbox.
  echo.
  pause
  exit /b 1
)

echo  [*] Installing Python 3.12 (silent install)...
"%INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_pip=1

:: Refresh PATH
set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
if not exist "%PYTHON_EXE%" (
  set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe
)

if not exist "%PYTHON_EXE%" (
  echo  [ERROR] Installation may have failed. Try running as Administrator.
  echo  Manual download: https://www.python.org/downloads/
  pause
  exit /b 1
)

echo  [+] Python installed successfully!

:found_python
echo  [+] Python found: %PYTHON_EXE%
"%PYTHON_EXE%" --version

:: ── Step 3: Install dependencies ────────────────────────────
echo.
echo  [*] Installing Python dependencies...
echo      (This may take 1-3 minutes on first run)
echo.

"%PYTHON_EXE%" -m pip install --upgrade pip --quiet
"%PYTHON_EXE%" -m pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
  echo.
  echo  [WARN] Some packages had issues. Trying with --user flag...
  "%PYTHON_EXE%" -m pip install -r requirements.txt --user
)

echo.
echo  [+] Dependencies installed!

:: ── Step 4: Launch the application ──────────────────────────
echo.
echo  [*] Starting Smart Business Idea Generator...
echo  [*] URL: http://localhost:5000
echo  [*] Press Ctrl+C to stop the server
echo.

:: Open browser after 3 seconds
start "" cmd /c "timeout /t 3 >nul && start http://localhost:5000"

"%PYTHON_EXE%" app.py

pause
