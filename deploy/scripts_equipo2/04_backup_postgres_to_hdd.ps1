<#
.SYNOPSIS
    Respalda la base de datos PostgreSQL alojada en el SSD del Equipo 2 hacia el HDD de 1 TB,
    calcula su huella digital SHA-256, aplica rotación automática y permite registrar
    una tarea programada semanal en Windows 10.
#>

param(
    [string]$BackupDir = "D:\SentinelNutri\hdd\backups",
    [int]$RetentionDays = 30,
    [int]$MinKeepCount = 5,
    [switch]$RegisterWeeklyTask
)

$ErrorActionPreference = "Stop"

if ($RegisterWeeklyTask) {
    $ScriptPath = $MyInvocation.MyCommand.Path
    $TaskName = "SentinelNutri_Weekly_Postgres_Backup_HDD"
    $Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""
    $Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 2:00AM
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Description "Respaldo semanal PostgreSQL 16 (SSD) -> HDD 1 TB con huella SHA-256 (SentinelNutri-HVC)" -Force | Out-Null
    Write-Host "[OK] Tarea programada '$TaskName' registrada en Windows Task Scheduler (Domingos 02:00 AM)." -ForegroundColor Green
    exit 0
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = Join-Path $BackupDir "sentinelnutri_hvc_$Timestamp.sql"

if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

Write-Host "[BACKUP] Volcando PostgreSQL (SSD) -> HDD 1TB ($BackupFile)..." -ForegroundColor Cyan
docker exec sentinelnutri_postgres pg_dump -U sentinel_user -d sentinelnutri_hvc > $BackupFile

$FileInfo = Get-Item $BackupFile
if ($FileInfo.Length -le 0) {
    Write-Error "El archivo de respaldo se generó vacío: $BackupFile"
    exit 1
}

$Hash = (Get-FileHash -Path $BackupFile -Algorithm SHA256).Hash.ToLower()
$HashFile = "$BackupFile.sha256"
Set-Content -Path $HashFile -Value "$Hash  $($FileInfo.Name)" -Encoding UTF8

# Rotación automática: conserva al menos $MinKeepCount respaldos recientes y elimina los > $RetentionDays días
$AllBackups = Get-ChildItem -Path $BackupDir -Filter "sentinelnutri_hvc_*.sql" | Sort-Object LastWriteTime -Descending
if ($AllBackups.Count -gt $MinKeepCount) {
    $Cutoff = (Get-Date).AddDays(-$RetentionDays)
    $ToPrune = $AllBackups | Select-Object -Skip $MinKeepCount | Where-Object { $_.LastWriteTime -lt $Cutoff }
    foreach ($Old in $ToPrune) {
        Remove-Item $Old.FullName -Force -ErrorAction SilentlyContinue
        Remove-Item "$($Old.FullName).sha256" -Force -ErrorAction SilentlyContinue
        Write-Host "[ROTACIÓN] Eliminado respaldo antiguo: $($Old.Name)" -ForegroundColor Yellow
    }
}

Write-Host "[OK] Respaldo completado en HDD ($([math]::Round($FileInfo.Length / 1MB, 2)) MB) | SHA-256: $($Hash.Substring(0, 16))..." -ForegroundColor Green
