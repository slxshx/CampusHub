$ErrorActionPreference = "Stop"

Write-Host "======================================"
Write-Host "       CampusHub Windows Setup"
Write-Host "======================================"
Write-Host ""

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $ProjectRoot "backend"
$NginxDir = Join-Path $ProjectRoot "nginx"

$EnvFile = Join-Path $BackendDir ".env"
$EnvExample = Join-Path $BackendDir ".env.example"
$SchemaFile = Join-Path $BackendDir "scripts\schema.sql"

$ToolsDir = Join-Path $ProjectRoot ".tools"
$NginxHome = Join-Path $ToolsDir "nginx"

$NginxVersion = "1.31.5"
$NginxZip = Join-Path $ToolsDir "nginx.zip"
$NginxDownload = "https://nginx.org/download/nginx-$NginxVersion.zip"

Write-Host "Projektverzeichnis:"
Write-Host $ProjectRoot
Write-Host ""

# --------------------------------------------------
# WinGet
# --------------------------------------------------

Write-Host "[1/7] Prüfe WinGet..."

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "FEHLER: WinGet wurde nicht gefunden."
    Write-Host "Bitte installiere den Windows App Installer."
    exit 1
}

Write-Host "✓ WinGet gefunden"
Write-Host ""

# --------------------------------------------------
# Python
# --------------------------------------------------

Write-Host "[2/7] Prüfe Python..."

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python wurde nicht gefunden. Installiere Python..."

    winget install `
        --id Python.Python.3.12 `
        -e `
        --accept-package-agreements `
        --accept-source-agreements

    Write-Host ""
    Write-Host "Python wurde installiert."
    Write-Host "Bitte öffne PowerShell neu und starte das Setup erneut."
    exit 0
}

Write-Host "✓ Python gefunden"
Write-Host ""

# --------------------------------------------------
# uv
# --------------------------------------------------

Write-Host "[3/7] Prüfe uv..."

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Installiere uv..."

    winget install `
        --id astral-sh.uv `
        -e `
        --accept-package-agreements `
        --accept-source-agreements

    Write-Host ""
    Write-Host "uv wurde installiert."
    Write-Host "Bitte PowerShell neu öffnen und Setup erneut starten."
    exit 0
}

Write-Host "✓ uv gefunden"
Write-Host ""

# --------------------------------------------------
# PostgreSQL
# --------------------------------------------------

Write-Host "[4/7] Prüfe PostgreSQL..."

$Psql = Get-Command psql -ErrorAction SilentlyContinue

if (-not $Psql) {
    $DefaultPsql = "C:\Program Files\PostgreSQL\17\bin\psql.exe"

    if (Test-Path $DefaultPsql) {
        $Psql = $DefaultPsql
    }
}

if (-not $Psql) {
    Write-Host "PostgreSQL 17 wurde nicht gefunden."
    Write-Host "Der PostgreSQL-Installer wird jetzt gestartet."
    Write-Host ""
    Write-Host "WICHTIG:"
    Write-Host "Merke dir das Passwort für den Benutzer 'postgres'."
    Write-Host ""

    winget install `
        --id PostgreSQL.PostgreSQL.17 `
        -e `
        --accept-package-agreements `
        --accept-source-agreements

    Write-Host ""
    Write-Host "PostgreSQL wurde installiert."
    Write-Host "Bitte PowerShell neu öffnen und Setup erneut starten."
    exit 0
}

if ($Psql -is [System.Management.Automation.ApplicationInfo]) {
    $PsqlExe = $Psql.Source
}
else {
    $PsqlExe = $Psql
}

Write-Host "✓ PostgreSQL gefunden"
Write-Host ""

# --------------------------------------------------
# Backend
# --------------------------------------------------

Write-Host "[5/7] Bereite Backend vor..."

if (-not (Test-Path $EnvFile)) {
    if (-not (Test-Path $EnvExample)) {
        Write-Host "FEHLER: backend/.env.example fehlt."
        exit 1
    }

    Copy-Item $EnvExample $EnvFile

    Write-Host "✓ backend/.env wurde erstellt"
    Write-Host ""
    Write-Host "Bitte DB_PASSWORD in backend/.env setzen."
    Write-Host "Danach Setup erneut starten."

    exit 0
}

Push-Location $BackendDir
uv sync
Pop-Location

Write-Host "✓ Backend-Abhängigkeiten installiert"
Write-Host ""

# --------------------------------------------------
# Env lesen
# --------------------------------------------------

$EnvValues = @{}

Get-Content $EnvFile | ForEach-Object {
    $Line = $_.Trim()

    if (-not $Line -or $Line.StartsWith("#")) {
        return
    }

    $Parts = $Line -split "=", 2

    if ($Parts.Count -eq 2) {
        $EnvValues[$Parts[0].Trim()] = $Parts[1].Trim()
    }
}

$DbHost = $EnvValues["DB_HOST"]
$DbPort = $EnvValues["DB_PORT"]
$DbName = $EnvValues["DB_NAME"]
$DbUser = $EnvValues["DB_USER"]
$DbPassword = $EnvValues["DB_PASSWORD"]

$TestDbName = "${DbName}_test"

if (-not $DbPassword -or $DbPassword -eq "CHANGE_ME") {
    Write-Host "FEHLER: DB_PASSWORD in backend/.env setzen."
    exit 1
}

# --------------------------------------------------
# DB Setup
# --------------------------------------------------

Write-Host "[6/7] Bereite Datenbanken vor..."
Write-Host ""

$SecurePassword = Read-Host `
    "PostgreSQL-Passwort für Benutzer 'postgres'" `
    -AsSecureString

$PostgresPassword = [System.Net.NetworkCredential]::new(
    "",
    $SecurePassword
).Password

$env:PGPASSWORD = $PostgresPassword

$RoleExists = & $PsqlExe `
    -U postgres `
    -h localhost `
    -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DbUser'"

if ($RoleExists -match "1") {
    Write-Host "✓ Rolle '$DbUser' existiert bereits"
}
else {
    & $PsqlExe `
        -U postgres `
        -h localhost `
        -c "CREATE ROLE $DbUser WITH LOGIN PASSWORD '$DbPassword';"

    Write-Host "✓ Rolle '$DbUser' erstellt"
}

foreach ($Database in @($DbName, $TestDbName)) {

    $DatabaseExists = & $PsqlExe `
        -U postgres `
        -h localhost `
        -tAc "SELECT 1 FROM pg_database WHERE datname='$Database'"

    if ($DatabaseExists -match "1") {
        Write-Host "✓ Datenbank '$Database' existiert bereits"
    }
    else {
        & $PsqlExe `
            -U postgres `
            -h localhost `
            -c "CREATE DATABASE $Database OWNER $DbUser;"

        Write-Host "✓ Datenbank '$Database' erstellt"
    }
}

Remove-Item Env:\PGPASSWORD

if (-not (Test-Path $SchemaFile)) {
    Write-Host "FEHLER: backend/scripts/schema.sql fehlt."
    exit 1
}

$env:PGPASSWORD = $DbPassword

foreach ($Database in @($DbName, $TestDbName)) {

    $SchemaExists = & $PsqlExe `
        -U $DbUser `
        -h $DbHost `
        -p $DbPort `
        -d $Database `
        -tAc "SELECT to_regclass('public.devices');"

    if ($SchemaExists -match "devices") {
        Write-Host "✓ Schema in '$Database' bereits vorhanden"
    }
    else {
        & $PsqlExe `
            -U $DbUser `
            -h $DbHost `
            -p $DbPort `
            -d $Database `
            -f $SchemaFile

        Write-Host "✓ Schema in '$Database' importiert"
    }
}

Remove-Item Env:\PGPASSWORD

# --------------------------------------------------
# Nginx
# --------------------------------------------------

Write-Host ""
Write-Host "[7/7] Bereite Nginx vor..."

New-Item `
    -ItemType Directory `
    -Force `
    -Path $ToolsDir | Out-Null

if (-not (Test-Path $NginxHome)) {

    Write-Host "Lade Nginx $NginxVersion..."

    Invoke-WebRequest `
        -Uri $NginxDownload `
        -OutFile $NginxZip

    Expand-Archive `
        -Path $NginxZip `
        -DestinationPath $ToolsDir `
        -Force

    Move-Item `
        (Join-Path $ToolsDir "nginx-$NginxVersion") `
        $NginxHome

    Remove-Item $NginxZip

    Write-Host "✓ Nginx heruntergeladen"
}

$FrontendPath = (
    Join-Path $ProjectRoot "frontend"
).Replace("\", "/")

$WindowsNginxConfig = @"
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    include mime.types;
    default_type application/octet-stream;

    sendfile on;

    server {
        listen 8081;

        server_name localhost;

        root $FrontendPath;

        index index.html;

        location / {
            try_files `$uri `$uri/ /index.html;
        }

        location /api/ {
            proxy_pass http://127.0.0.1:8000/;

            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
            proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto `$scheme;
        }
    }
}
"@

$NginxConfigPath = Join-Path $NginxHome "conf\nginx.conf"

Set-Content `
    -Path $NginxConfigPath `
    -Value $WindowsNginxConfig

$NginxExe = Join-Path $NginxHome "nginx.exe"

Push-Location $NginxHome

& $NginxExe -t

$Running = Get-Process nginx -ErrorAction SilentlyContinue

if ($Running) {
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
Write-Host "======================================"
Write-Host "       CampusHub Setup beendet"
Write-Host "======================================"
Write-Host ""
Write-Host "Frontend:"
Write-Host "  http://localhost:8081"
Write-Host ""
Write-Host "Backend:"
Write-Host "  cd backend"
Write-Host "  uv run uvicorn campushub.__main__:app --reload"
Write-Host ""
Write-Host "Swagger:"
Write-Host "  http://localhost:8081/api/docs"
Write-Host ""
