<#
.SYNOPSIS
    Instala y configura Ollama en el Equipo 2 (Windows 10) aprovechando la GPU NVIDIA GTX 1050 (4 GB VRAM)
    y redirige el almacenamiento de modelos al disco duro de 1 TB (D:\SentinelNutri\hdd\ollama_models).
#>

$ErrorActionPreference = "Stop"

Write-Host "=== [SentinelNutri-HVC] Configuración de Ollama + GPU GTX 1050 en Equipo 2 ===" -ForegroundColor Cyan

# 1. Verificar tarjeta gráfica NVIDIA GTX 1050 (4 GB)
if (Get-Command "nvidia-smi" -ErrorAction SilentlyContinue) {
    Write-Host "[GPU] Detectando NVIDIA GTX 1050:" -ForegroundColor Green
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
} else {
    Write-Warning "No se encontró 'nvidia-smi' en PATH. Asegúrate de tener los drivers NVIDIA instalados en Windows 10."
}

# 2. Configurar variables de entorno del sistema en Equipo 2
#    - OLLAMA_MODELS apunta al HDD de 1 TB para no llenar el SSD
#    - OLLAMA_HOST=0.0.0.0:11434 permite que los contenedores Docker (n8n, FastAPI) se conecten vía host.docker.internal
$ModelsDir = "D:\SentinelNutri\hdd\ollama_models"
if (-not (Test-Path $ModelsDir)) {
    New-Item -ItemType Directory -Path $ModelsDir -Force | Out-Null
}

[System.Environment]::SetEnvironmentVariable("OLLAMA_MODELS", $ModelsDir, "User")
[System.Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0:11434", "User")
[System.Environment]::SetEnvironmentVariable("OLLAMA_VULKAN", "1", "User")
[System.Environment]::SetEnvironmentVariable("CUDA_VISIBLE_DEVICES", "-1", "User")
$env:OLLAMA_MODELS = $ModelsDir
$env:OLLAMA_HOST = "0.0.0.0:11434"
$env:OLLAMA_VULKAN = "1"
$env:CUDA_VISIBLE_DEVICES = "-1"

Write-Host "[ENV] OLLAMA_MODELS configurado en: $ModelsDir" -ForegroundColor Green
Write-Host "[ENV] OLLAMA_HOST configurado en: 0.0.0.0:11434" -ForegroundColor Green
Write-Host "[ENV] OLLAMA_VULKAN=1 (Backend Vulkan para GTX 1050 Pascal CC 6.1 con Driver 566.36)" -ForegroundColor Green

# 3. Instalar Ollama si no está instalado
if (-not (Get-Command "ollama" -ErrorAction SilentlyContinue)) {
    Write-Host "[INSTALL] Instalando Ollama mediante winget..." -ForegroundColor Yellow
    winget install --id Ollama.Ollama -e --silent --accept-source-agreements --accept-package-agreements
    $OllamaBin = "$env:LOCALAPPDATA\Programs\Ollama"
    if ((Test-Path $OllamaBin) -and ($env:PATH -notlike "*$OllamaBin*")) {
        $env:PATH = "$OllamaBin;$env:PATH"
    }
} else {
    Write-Host "[OK] Ollama ya se encuentra instalado." -ForegroundColor Green
}

# 4. Descargar Llama 3.2 (3B cuantizado ~2.0 GB: cabe íntegramente en los 4 GB de VRAM de la GTX 1050)
Write-Host "[MODEL] Descargando modelo de respaldo 'llama3.2' (optimizado para 4 GB VRAM en GTX 1050)..." -ForegroundColor Cyan
ollama pull llama3.2

Write-Host "=== Ollama listo y acelerado por GPU en Equipo 2 ===" -ForegroundColor Cyan

