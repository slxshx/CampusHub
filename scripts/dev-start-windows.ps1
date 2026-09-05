$ErrorActionPreference = "Stop"

Write-Host "======================================"
Write-Host "      CampusHub Dev Start Windows"
Write-Host "======================================"
Write-Host ""

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $ProjectRoot "backend"
$NginxHome = Join-Path $ProjectRoot ".tools\nginx"
$NginxExe = Join-Path $NginxHome "nginx.exe"


Write-Host "[1/3] Prüfe PostgreSQL..."

$PostgresService = Get-Service |
    Where-Object {
        $_.Name -like "postgresql*"
    } |
    Select-Object -First 1

if (-not $PostgresService) {
    Write-Host "FEHLER: PostgreSQL-Service wurde nicht gefunden."
    Write-Host "Bitte zuerst setup-windows.ps1 ausführen."
    exit 1
}

if ($PostgresService.Status -ne "Running") {
    Start-Service $PostgresService.Name
}

Write-Host "✓ PostgreSQL läuft"
Write-Host ""


Write-Host "[2/3] Starte / lade Nginx..."

if (-not (Test-Path $NginxExe)) {
    Write-Host "FEHLER: Nginx wurde nicht gefunden."
    Write-Host "Bitte zuerst setup-windows.ps1 ausführen."
    exit 1
}

Push-Location $NginxHome

& $NginxExe -t

$NginxRunning = Get-Process nginx -ErrorAction SilentlyContinue

if ($NginxRunning) {
    & $NginxExe -s reload

    Write-Host "✓ Nginx neu geladen"
}
else {
    Start-Process $NginxExe `
        -WorkingDirectory $NginxHome

    Write-Host "✓ Nginx gestartet"
}

Pop-Location

Write-Host ""


Write-Host "[3/3] Starte FastAPI..."
Write-Host ""
Write-Host "CampusHub:"
Write-Host "  http://localhost:8081"
Write-Host ""
Write-Host "Swagger:"
Write-Host "  http://localhost:8081/api/docs"
Write-Host ""
Write-Host "Backend wird mit Ctrl+C beendet."
Write-Host ""

Set-Location $BackendDir

uv run uvicorn campushub.__main__:app --reload
