<#
.SYNOPSIS
    Smart Business Idea Generator — Complete Setup & Run Script
    Installs Python 3.12 if missing, installs all dependencies, launches the app.
#>

$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "Smart Business Idea Generator Setup"

Write-Host ""
Write-Host "  ============================================================" -ForegroundColor Cyan
Write-Host "   Smart Business Idea Generator" -ForegroundColor White
Write-Host "   Powered by IBM Granite AI · Multi-Agent System" -ForegroundColor Gray
Write-Host "  ============================================================" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: Find Python ──────────────────────────────────────────────────────
function Find-Python {
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python39\python.exe",
        "C:\Python313\python.exe",
        "C:\Python312\python.exe",
        "C:\Python311\python.exe",
        "C:\Python310\python.exe",
        "C:\Python39\python.exe",
        "$env:USERPROFILE\Anaconda3\python.exe",
        "$env:USERPROFILE\miniconda3\python.exe",
        "C:\ProgramData\Anaconda3\python.exe",
        "C:\Anaconda3\python.exe",
        "C:\miniconda3\python.exe"
    )
    foreach ($p in $candidates) {
        if (Test-Path $p) { return $p }
    }
    # Check PATH
    $fromPath = Get-Command "python" -ErrorAction SilentlyContinue
    if ($fromPath -and $fromPath.Source -notmatch "WindowsApps") {
        return $fromPath.Source
    }
    return $null
}

$pythonExe = Find-Python

# ── Step 2: Install Python if not found ─────────────────────────────────────
if (-not $pythonExe) {
    Write-Host "  [!] Python not found on this system." -ForegroundColor Yellow
    Write-Host "  [*] Downloading Python 3.12.7 from python.org..." -ForegroundColor Cyan

    $installerPath = "$env:TEMP\python-3.12.7-amd64.exe"
    $downloadUrl   = "https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe"

    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $wc = New-Object Net.WebClient
        $wc.DownloadFile($downloadUrl, $installerPath)
        Write-Host "  [+] Download complete." -ForegroundColor Green
    } catch {
        Write-Host ""
        Write-Host "  [ERROR] Download failed: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "  Please install Python manually from: https://www.python.org/downloads/" -ForegroundColor Yellow
        Write-Host "  IMPORTANT: Check 'Add Python to PATH' during installation." -ForegroundColor Yellow
        Write-Host ""
        Read-Host "  Press Enter to exit"
        exit 1
    }

    Write-Host "  [*] Running Python installer (this may take 1-2 minutes)..." -ForegroundColor Cyan
    $installArgs = "/quiet", "InstallAllUsers=0", "PrependPath=1", "Include_test=0", "Include_pip=1", "Include_launcher=1"
    Start-Process -FilePath $installerPath -ArgumentList $installArgs -Wait

    # Refresh search after install
    Start-Sleep -Seconds 2
    $pythonExe = Find-Python

    if (-not $pythonExe) {
        # Last fallback — try reloading PATH from registry
        $machinePath = [System.Environment]::GetEnvironmentVariable("PATH", "Machine")
        $userPath    = [System.Environment]::GetEnvironmentVariable("PATH", "User")
        $env:PATH    = "$userPath;$machinePath"
        $pythonExe   = Find-Python
    }

    if (-not $pythonExe) {
        Write-Host ""
        Write-Host "  [ERROR] Installation may have failed or PATH not updated yet." -ForegroundColor Red
        Write-Host "  Please open a NEW terminal window and run this script again." -ForegroundColor Yellow
        Write-Host "  Or install manually: https://www.python.org/downloads/" -ForegroundColor Yellow
        Read-Host "  Press Enter to exit"
        exit 1
    }

    Write-Host "  [+] Python installed successfully!" -ForegroundColor Green
}

# ── Step 3: Verify Python version ────────────────────────────────────────────
$versionOutput = & $pythonExe --version 2>&1
Write-Host "  [+] Using: $versionOutput  ($pythonExe)" -ForegroundColor Green
Write-Host ""

# ── Step 4: Upgrade pip ───────────────────────────────────────────────────────
Write-Host "  [*] Upgrading pip..." -ForegroundColor Cyan
& $pythonExe -m pip install --upgrade pip --quiet
Write-Host "  [+] pip upgraded." -ForegroundColor Green

# ── Step 5: Install requirements ─────────────────────────────────────────────
$reqFile = Join-Path $PSScriptRoot "requirements.txt"
Write-Host ""
Write-Host "  [*] Installing dependencies from requirements.txt..." -ForegroundColor Cyan
Write-Host "      (First run takes 1-3 minutes)" -ForegroundColor Gray
Write-Host ""

try {
    & $pythonExe -m pip install -r $reqFile
    if ($LASTEXITCODE -ne 0) { throw "pip install exited with code $LASTEXITCODE" }
    Write-Host ""
    Write-Host "  [+] All dependencies installed!" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "  [WARN] Some packages may have had issues: $_" -ForegroundColor Yellow
    Write-Host "  [*] Retrying with --user flag..." -ForegroundColor Cyan
    & $pythonExe -m pip install -r $reqFile --user
}

# ── Step 6: Launch the application ───────────────────────────────────────────
$appFile = Join-Path $PSScriptRoot "app.py"
Write-Host ""
Write-Host "  ============================================================" -ForegroundColor Cyan
Write-Host "   Starting Smart Business Idea Generator..." -ForegroundColor White
Write-Host "   URL: http://localhost:5000" -ForegroundColor Green
Write-Host "   Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host "  ============================================================" -ForegroundColor Cyan
Write-Host ""

# Open browser after 3-second delay
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 3
    Start-Process "http://localhost:5000"
} | Out-Null

Set-Location $PSScriptRoot
& $pythonExe $appFile
