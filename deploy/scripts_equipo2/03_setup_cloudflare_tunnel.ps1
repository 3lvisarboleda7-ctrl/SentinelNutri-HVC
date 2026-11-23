<#
.SYNOPSIS
    Configuración y despliegue automatizado de Cloudflare Tunnel en el Equipo 2 (Windows 10).
.DESCRIPTION
    Soporta dos modos sin abrir puertos en el router y sin interferir con otros proyectos Docker:
    1. Modo Túnel Nombrado (Zero Trust, persistente): usa CLOUDFLARE_TUNNEL_TOKEN en config/.env.equipo2
       y levanta únicamente el servicio `cloudflared` del proyecto `-p sentinelnutri`.
    2. Modo Quick Tunnel (`-QuickTunnel`, sin dominio propio): levanta únicamente el contenedor aislado
       `sentinelnutri_quick_tunnel` en `sentinelnutri_msv_net`, detecta la URL HTTPS `*.trycloudflare.com`,
       sincroniza `N8N_PUBLIC_WEBHOOK_URL` en `config/.env.equipo2` y recrea solo `n8n`.
#>

param(
    [string]$TunnelToken = $env:CLOUDFLARE_TUNNEL_TOKEN,
    [switch]$QuickTunnel,
    [string]$EnvFile = "config/.env.equipo2",
    [string]$ComposeFile = "deploy/docker-compose.equipo2.yml"
)

$ErrorActionPreference = "Stop"

Write-Host "=== [SentinelNutri-HVC] Gestión de Cloudflare Tunnel (Equipo 2) ===" -ForegroundColor Cyan

# Leer CLOUDFLARE_TUNNEL_TOKEN desde config/.env.equipo2 si no vino por parámetro ni entorno
if ([string]::IsNullOrWhiteSpace($TunnelToken) -and (Test-Path $EnvFile)) {
    $tokenLine = Get-Content $EnvFile | Where-Object { $_ -match '^\s*CLOUDFLARE_TUNNEL_TOKEN=' } | Select-Object -First 1
    if ($tokenLine) {
        $TunnelToken = ($tokenLine -split '=', 2)[1].Trim().Trim('"')
    }
}

if ($QuickTunnel) {
    Write-Host "[Modo Quick Tunnel] Iniciando túnel HTTPS temporal sobre sentinelnutri_msv_net..." -ForegroundColor Yellow

    # Eliminar solo el contenedor de Quick Tunnel propio de SentinelNutri (nunca tocar otros proyectos)
    $existing = docker ps -a --filter "name=^/sentinelnutri_quick_tunnel$" --format "{{.Names}}"
    if ($existing) {
        docker rm -f sentinelnutri_quick_tunnel | Out-Null
    }

    docker run -d `
        --name sentinelnutri_quick_tunnel `
        --network sentinelnutri_msv_net `
        --restart unless-stopped `
        cloudflare/cloudflared:latest `
        tunnel --no-autoupdate --url http://n8n:5678 | Out-Null

    $publicUrl = $null
    for ($i = 0; $i -lt 20; $i++) {
        Start-Sleep -Seconds 1
        $logs = docker logs sentinelnutri_quick_tunnel 2>&1 | Out-String
        if ($logs -match 'https://[a-z0-9-]+\.trycloudflare\.com') {
            $publicUrl = $Matches[0]
            break
        }
    }

    if (-not $publicUrl) {
        Write-Error "No se pudo obtener la URL *.trycloudflare.com en 20 s. Revise: docker logs sentinelnutri_quick_tunnel"
        exit 1
    }

    Write-Host "[OK] Quick Tunnel activo: $publicUrl -> http://n8n:5678" -ForegroundColor Green

    if (Test-Path $EnvFile) {
        $content = Get-Content $EnvFile -Raw
        $targetLine = "N8N_PUBLIC_WEBHOOK_URL=$publicUrl/"
        if ($content -match '(?m)^N8N_PUBLIC_WEBHOOK_URL=.*$') {
            $content = [regex]::Replace($content, '(?m)^N8N_PUBLIC_WEBHOOK_URL=.*$', $targetLine)
        } else {
            $content = $content.TrimEnd() + "`r`n$targetLine`r`n"
        }
        Set-Content -Path $EnvFile -Value $content -NoNewline
        Write-Host "[OK] Sincronizado $targetLine en $EnvFile" -ForegroundColor Green

        docker compose -p sentinelnutri -f $ComposeFile --env-file $EnvFile up -d --no-deps --force-recreate n8n
        Write-Host "[OK] Servicio n8n recreado únicamente con la nueva URL pública de webhooks HITL." -ForegroundColor Green
    }
    exit 0
}

if ([string]::IsNullOrWhiteSpace($TunnelToken)) {
    Write-Host "Estado: Túnel Nombrado (Zero Trust) PENDIENTE de CLOUDFLARE_TUNNEL_TOKEN." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Opción A — Túnel Nombrado permanente (requiere dominio propio en Cloudflare):" -ForegroundColor Cyan
    Write-Host "  1. Ingresa a https://one.dash.cloudflare.com/ -> Networks -> Tunnels"
    Write-Host "  2. Crea un túnel 'sentinelnutri-hvc-equipo2' (Conector Cloudflared)"
    Write-Host "  3. Copia el token eyJhIjoi... en $EnvFile (CLOUDFLARE_TUNNEL_TOKEN=...)"
    Write-Host "  4. En 'Public Hostname', apunta tu subdominio (ej. n8n.tudominio.com) hacia: http://n8n:5678"
    Write-Host "  5. Vuelve a ejecutar este script sin parámetros para levantar 'sentinelnutri_cloudflare_tunnel'."
    Write-Host ""
    Write-Host "Opción B — Quick Tunnel gratuito inmediato (sin dominio propio):" -ForegroundColor Cyan
    Write-Host "  .\deploy\scripts_equipo2\03_setup_cloudflare_tunnel.ps1 -QuickTunnel"
    exit 0
}

Write-Host "[OK] CLOUDFLARE_TUNNEL_TOKEN detectado. Levantando únicamente 'cloudflared' en -p sentinelnutri..." -ForegroundColor Green
docker compose -p sentinelnutri -f $ComposeFile --env-file $EnvFile up -d --no-deps cloudflared
docker ps --filter "name=sentinelnutri_cloudflare_tunnel" --format "table {{.Names}}\t{{.Status}}"
