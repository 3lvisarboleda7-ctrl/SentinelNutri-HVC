<#
.SYNOPSIS
    Respalda la base de datos PostgreSQL alojada en el SSD del Equipo 2 hacia el HDD de 1 TB.
#>

$ErrorActionPreference = "Stop"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupDir = "D:\SentinelNutri\hdd\backups"
$BackupFile = Join-Path $BackupDir "sentinelnutri_hvc_$Timestamp.sql"

if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

Write-Host "[BACKUP] Volcando PostgreSQL (SSD) -> HDD 1TB ($BackupFile)..." -ForegroundColor Cyan
docker exec sentinelnutri_postgres pg_dump -U sentinel_user -d sentinelnutri_hvc > $BackupFile
Write-Host "[OK] Respaldo completado exitosamente en el HDD." -ForegroundColor Green

