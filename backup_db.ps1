<#
.SYNOPSIS
    Script de backup do banco de dados da ENDE Platform
.DESCRIPTION
    Exporta o banco de dados SQLite para um ficheiro .sql
    e cria um arquivo ZIP do projecto.
#>

param(
    [string]$OutputDir = "."
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host "=== ENDE Platform - Backup ===" -ForegroundColor Cyan

# 1. Backup do banco SQLite
$dbPath = Join-Path $ProjectRoot "db.sqlite3"
if (Test-Path $dbPath) {
    $backupFile = Join-Path $OutputDir "backup_ende_$Timestamp.sql"
    Write-Host "[1/3] Exportando banco de dados..." -ForegroundColor Yellow
    
    # Usar o Django para fazer dump dos dados
    & "$ProjectRoot\venv\Scripts\python.exe" manage.py dumpdata --exclude auth.permission --exclude contenttypes > $backupFile 2>$null
    
    if ($?) {
        Write-Host "      Backup salvo em: $backupFile" -ForegroundColor Green
    } else {
        Write-Host "      Erro ao exportar banco. Copiando ficheiro directamente..." -ForegroundColor Yellow
        Copy-Item $dbPath (Join-Path $OutputDir "backup_ende_$Timestamp.db")
    }
} else {
    Write-Host "[1/3] Banco de dados não encontrado: $dbPath" -ForegroundColor Red
}

# 2. Backup dos media (se existir)
$mediaPath = Join-Path $ProjectRoot "media"
if (Test-Path $mediaPath) {
    Write-Host "[2/3] Copiando ficheiros media..." -ForegroundColor Yellow
    $mediaBackup = Join-Path $OutputDir "media_$Timestamp"
    Copy-Item -Recurse $mediaPath $mediaBackup
}

# 3. Listar ficheiros do projecto
Write-Host "[3/3] Projecto preparado para exportação..." -ForegroundColor Yellow
Write-Host "      Execute o seguinte comando para criar o ZIP:" -ForegroundColor Cyan
Write-Host "      git archive -o projeto_final_$Timestamp.zip HEAD" -ForegroundColor White

Write-Host "=== Backup Concluído ===" -ForegroundColor Cyan
