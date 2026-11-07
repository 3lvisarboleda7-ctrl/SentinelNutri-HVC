<#
.SYNOPSIS
    Aprovisiona las rutas separadas en el SSD (C:\) y el HDD de 1 TB (D:\) en el Equipo 2 (Servidor Local Windows 10).
.DESCRIPTION
    Según la Tabla 3 del Perfil de Proyecto (SentinelNutri-HVC):
    - SSD (447 GB): Aloja contenedores Docker, motor PostgreSQL activo y configuración de n8n.
    - HDD (1 TB): Aloja archivos crudos descargados (/raw), respaldos (/backups), modelos entrenados (/models) y pesos de Ollama.
#>

$ErrorActionPreference = "Stop"

$SsdPaths = @(
    "C:\SentinelNutri\ssd\postgres_data",
    "C:\SentinelNutri\ssd\n8n_data"
)

$HddPaths = @(
    "D:\SentinelNutri\hdd\raw\sien_his",
    "D:\SentinelNutri\hdd\raw\endes_inei",
    "D:\SentinelNutri\hdd\raw\inei_pobreza",
    "D:\SentinelNutri\hdd\raw\mef_pan",
    "D:\SentinelNutri\hdd\raw\midis_programas",
    "D:\SentinelNutri\hdd\raw\senamhi_clima",
    "D:\SentinelNutri\hdd\diresa_convenio_ley29733",
    "D:\SentinelNutri\hdd\models",
    "D:\SentinelNutri\hdd\backups",
    "D:\SentinelNutri\hdd\ollama_models"
)

Write-Host "=== [SentinelNutri-HVC] Configurando estructura SSD + HDD en Equipo 2 ===" -ForegroundColor Cyan

foreach ($path in $SsdPaths) {
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Host "[SSD] Creado: $path" -ForegroundColor Green
    } else {
        Write-Host "[SSD] Ya existe: $path" -ForegroundColor Gray
    }
}

foreach ($path in $HddPaths) {
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Host "[HDD 1TB] Creado: $path" -ForegroundColor Yellow
    } else {
        Write-Host "[HDD 1TB] Ya existe: $path" -ForegroundColor Gray
    }
}

$RepoModel = Join-Path $PSScriptRoot "..\..\data\models\catboost_dci_hvc.cbm"
if (Test-Path $RepoModel) {
    Copy-Item $RepoModel "D:\SentinelNutri\hdd\models\catboost_dci_hvc.cbm" -Force
    Write-Host "[HDD 1TB] Modelo CatBoost (catboost_dci_hvc.cbm) copiado a D:\SentinelNutri\hdd\models\" -ForegroundColor Green
}

Write-Host "Estructura lista en Equipo 2." -ForegroundColor Cyan

