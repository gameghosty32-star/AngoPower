<#
.SYNOPSIS
    Script de deploy para a ENDE Platform (ambiente Windows/desenvolvimento)
.DESCRIPTION
    Executa as etapas de deploy: verifica ambiente, instala dependências,
    aplica migrações, recolhe estáticos e inicia o servidor.
#>

param(
    [switch]$Prod,
    [switch]$MigrateOnly,
    [switch]$Start
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host "=== ENDE Platform - Deploy Script ===" -ForegroundColor Cyan

# 1. Verificar ambiente virtual
$venvPath = Join-Path $ProjectRoot "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "[1/6] Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv venv
} else {
    Write-Host "[1/6] Ambiente virtual encontrado." -ForegroundColor Green
}

# 2. Activar e instalar dependências
Write-Host "[2/6] Instalando dependências..." -ForegroundColor Yellow
& "$venvPath\Scripts\pip.exe" install django djangorestframework python-dotenv 2>$null

# 3. Verificar .env
$envFile = Join-Path $ProjectRoot ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "[3/6] Criando .env a partir de .env.example..." -ForegroundColor Yellow
    Copy-Item (Join-Path $ProjectRoot ".env.example") $envFile
} else {
    Write-Host "[3/6] .env encontrado." -ForegroundColor Green
}

# 4. Migrações
Write-Host "[4/6] Aplicando migrações..." -ForegroundColor Yellow
& "$venvPath\Scripts\python.exe" manage.py migrate

if ($MigrateOnly) {
    Write-Host "Migrações aplicadas. Encerrando." -ForegroundColor Green
    return
}

# 5. Recolher estáticos
Write-Host "[5/6] Recolhendo ficheiros estáticos..." -ForegroundColor Yellow
& "$venvPath\Scripts\python.exe" manage.py collectstatic --noinput

# 6. Iniciar servidor
if ($Start) {
    Write-Host "[6/6] Iniciando servidor em http://0.0.0.0:8000" -ForegroundColor Green
    & "$venvPath\Scripts\python.exe" manage.py runserver 0.0.0.0:8000
} else {
    Write-Host "[6/6] Servidor pronto. Execute:" -ForegroundColor Green
    Write-Host "  .\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000" -ForegroundColor Cyan
}

Write-Host "=== Concluído ===" -ForegroundColor Cyan
