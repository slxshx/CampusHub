$ErrorActionPreference = "Stop"

Write-Host "======================================"
Write-Host "       CampusHub Dev Stop Windows"
Write-Host "======================================"
Write-Host ""

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$NginxHome = Join-Path $ProjectRoot ".tools\nginx"
$NginxExe = Join-Path $NginxHome "nginx.exe"


Write-Host "[1/2] Stoppe Nginx..."

$NginxRunning = Get-Process nginx -ErrorAction SilentlyContinue

if ($NginxRunning) {
    if (Test-Path $NginxExe) {
        Push-Location $NginxHome
        & $NginxExe -s quit
        Pop-Location

        Write-Host "✓ Nginx gestoppt"
    }
    else {
        Write-Host "FEHLER: nginx.exe wurde nicht gefunden."
        exit 1
    }
}
else {
    Write-Host "✓ Nginx läuft bereits nicht"
}

Write-Host ""


Write-Host "[2/2] Stoppe PostgreSQL..."

$PostgresService = Get-Service |
    Where-Object {
        $_.Name -like "postgresql*"
    } |
    Select-Object -First 1

if ($PostgresService) {
    if ($PostgresService.Status -eq "Running") {
        Stop-Service $PostgresService.Name
        Write-Host "✓ PostgreSQL gestoppt"
    }
    else {
        Write-Host "✓ PostgreSQL läuft bereits nicht"
    }
}
else {
    Write-Host "FEHLER: PostgreSQL-Service wurde nicht gefunden."
    exit 1
}

Write-Host ""
Write-Host "======================================"
Write-Host "       CampusHub wurde gestoppt"
Write-Host "======================================"
