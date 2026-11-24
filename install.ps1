# CleanYourPhone Quick Installer for Windows PowerShell
$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   CleanYourPhone — Installation & Setup" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python 3 is required. Please install Python from https://python.org or winget install Python.Python.3.13"
    exit 1
}

# Check ADB
if (-not (Get-Command adb -ErrorAction SilentlyContinue)) {
    Write-Host "[*] ADB not found in PATH. Attempting automatic installation via winget..." -ForegroundColor Yellow
    winget install --id Google.PlatformTools --source winget --accept-package-agreements --accept-source-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# Install local package
Write-Host "[*] Installing CleanYourPhone CLI..." -ForegroundColor Green
python -m pip install -e . --no-warn-script-location

Write-Host ""
Write-Host "[SUCCESS] CleanYourPhone is installed!" -ForegroundColor Green
Write-Host "Run 'cleanyourphone --help' or 'cleanyourphone detect' to begin." -ForegroundColor Cyan
