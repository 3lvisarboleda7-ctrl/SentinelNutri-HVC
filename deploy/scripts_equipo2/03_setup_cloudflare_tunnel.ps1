<#
.SYNOPSIS
    Guía y verificación del túnel seguro Cloudflare Tunnel en el Equipo 2 (Windows 10).
.DESCRIPTION
    Publica los webhooks de n8n (:5678) bajo HTTPS sin abrir puertos en el router doméstico,
    permitiendo aprobar recomendaciones desde el celular (Telegram / Gmail) y protegiendo Windows 10.
#>

param(
    [string]$TunnelToken = $env:CLOUDFLARE_TUNNEL_TOKEN
)

Write-Host "=== [SentinelNutri-HVC] Verificación de Cloudflare Tunnel (Zero Trust) ===" -ForegroundColor Cyan

if ([string]::IsNullOrWhiteSpace($TunnelToken)) {
    Write-Host "Pasos para obtener el CLOUDFLARE_TUNNEL_TOKEN gratuito:" -ForegroundColor Yellow
    Write-Host "  1. Ingresa a https://one.dash.cloudflare.com/ -> Networks -> Tunnels"
    Write-Host "  2. Crea un túnel 'sentinelnutri-hvc-equipo2' (Conector Cloudflared)"
    Write-Host "  3. Copia el token eyJhIjoi... en config/.env.equipo2 (CLOUDFLARE_TUNNEL_TOKEN)"
    Write-Host "  4. En 'Public Hostname', apunta tu subdominio hacia el servicio interno: http://n8n:5678"
    exit 0
}

Write-Host "[OK] Token detectado. El contenedor 'sentinelnutri_cloudflare_tunnel' expondrá n8n de forma segura." -ForegroundColor Green

