$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Venv = "$ScriptDir\.venv\Scripts"
$Python = "$Venv\python.exe"
$Pip = "$Venv\pip.exe"

Write-Host "=== [1/5] Installing build deps ===" -ForegroundColor Cyan
& $Pip install pyinstaller pillow --quiet
if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
Write-Host "    OK" -ForegroundColor Green

Write-Host "=== [2/5] Generating icon ===" -ForegroundColor Cyan
& $Python "$ScriptDir\make_icon.py"
if ($LASTEXITCODE -ne 0) { throw "Icon generation failed" }
Write-Host "    OK" -ForegroundColor Green

Write-Host "=== [3/5] Cleaning previous build ===" -ForegroundColor Cyan
Remove-Item -Recurse -Force "$ScriptDir\dist" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$ScriptDir\build" -ErrorAction SilentlyContinue
Write-Host "    OK" -ForegroundColor Green

Write-Host "=== [4/5] Building .exe (PyInstaller) ===" -ForegroundColor Cyan
& "$Venv\pyinstaller.exe" "$ScriptDir\build.spec" --distpath "$ScriptDir\dist" --workpath "$ScriptDir\build"
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }
Write-Host "    OK" -ForegroundColor Green

Write-Host "=== [5/5] Preparing distribution ===" -ForegroundColor Cyan

$OutDir = "$ScriptDir\dist\ya360_manager"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$ExeSrc = "$ScriptDir\dist\ya360_manager.exe"
if (Test-Path $ExeSrc) {
    Move-Item -Force $ExeSrc "$OutDir\ya360_manager.exe"
}

$DataDir = "$OutDir\data"
New-Item -ItemType Directory -Force -Path $DataDir | Out-Null

$cfg = '{"theme": "light", "passwork_url": "https://your-passwork-domain.com", "passwork_api_token": "YOUR_PASSWORK_API_TOKEN_HERE", "passwork_search_tag": "yandex360token"}'
[System.IO.File]::WriteAllText("$DataDir\config.json", $cfg, [System.Text.Encoding]::UTF8)
Write-Host "    Created: $DataDir\config.json" -ForegroundColor Green

Write-Host ""
Write-Host "Build complete! Distribution: $OutDir" -ForegroundColor Yellow
Write-Host ""
Get-ChildItem -Recurse $OutDir | Select-Object FullName, Length | Format-Table -AutoSize
