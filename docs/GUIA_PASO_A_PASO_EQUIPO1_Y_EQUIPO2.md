# Guía Rápida Paso a Paso: Equipo 1 (Desarrollo + Colab) y Equipo 2 (Servidor Local)

Esta guía resume los comandos exactos para completar el despliegue entre tus dos computadoras.

---

## Parte A — En el `EQUIPO 1` (Esta Laptop Windows 11 · `Hostname: ELVIS`)

### Paso 1. Verificar estado de las credenciales y del nodo
```powershell
$env:PYTHONPATH="src;."; python -m sentinelnutri.cli whoami
$env:PYTHONPATH="src;."; python -m sentinelnutri.cli verify-env
```

### Paso 2. Repositorio en GitHub (Ya conectado y publicado)
- **URL del Repositorio:** `https://github.com/3lvisarboleda7-ctrl/SentinelNutri-HVC`
- Para subir futuros cambios desde el Equipo 1:
  ```powershell
  git add .
  git commit -m "chore: actualizacion"
  git push
  ```

### Paso 3. Ejecutar el entrenamiento pesado en Google Colab (Enlace directo en 1 clic)
1. Haz clic directamente en este enlace desde el navegador del **Equipo 1** (abre el notebook directamente desde tu GitHub en Google Colab sin tener que subir archivos manualmente):
   - **[Abrir `02_entrenamiento_catboost_shap_colab.ipynb` en Google Colab](https://colab.research.google.com/github/3lvisarboleda7-ctrl/SentinelNutri-HVC/blob/main/notebooks_colab/02_entrenamiento_catboost_shap_colab.ipynb)**
2. Pulsa **Entorno de ejecución $\rightarrow$ Ejecutar todas** (*Run all*).
3. Al finalizar la última celda, se descargará automáticamente el modelo `catboost_dci_hvc.cbm`.

---

## Parte B — En el `EQUIPO 2` (Servidor Local Windows 10 · SSD + HDD 1 TB · GTX 1050)

### Paso 1. Clonar el repositorio en el SSD (`C:\`) y crear carpetas en SSD + HDD (`D:\`)
Abre PowerShell como Administrador en el **Equipo 2**:
```powershell
git clone https://github.com/3lvisarboleda7-ctrl/SentinelNutri-HVC.git C:\SentinelNutri\repo
cd C:\SentinelNutri\repo
.\deploy\scripts_equipo2\01_setup_ssd_hdd_dirs.ps1
```

### Paso 2. Instalar Ollama acelerado por la GPU NVIDIA GTX 1050 (guardando modelos en el HDD `D:\`)
```powershell
.\deploy\scripts_equipo2\02_install_ollama_gpu.ps1
```

### Paso 3. Configurar `.env.equipo2` y levantar todos los contenedores en Docker
1. Copia la plantilla de variables de entorno:
   ```powershell
   Copy-Item config\.env.equipo2.example config\.env.equipo2
   notepad config\.env.equipo2
   ```
   *(Coloca allí tu `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `GMAIL_APP_PASSWORD` y `CLOUDFLARE_TUNNEL_TOKEN`).*
2. Levanta los servicios en Docker Desktop del Equipo 2:
   ```powershell
   docker compose -f deploy/docker-compose.equipo2.yml --env-file config/.env.equipo2 up -d --build
   ```

### Paso 4. Acceder desde el `EQUIPO 1` por Red Local (LAN)
Desde el navegador de tu **Equipo 1**, abre:
- **Orquestador Agéntico `n8n`:** `http://<IP_LAN_EQUIPO_2>:5678` (importa los 2 archivos JSON de `workflows_n8n/`).
- **Documentación Interactiva FastAPI (`/predict` y 6 Herramientas):** `http://<IP_LAN_EQUIPO_2>:8000/docs`
- **Dashboard Cibernético Streamlit (S2, S3, S3*, S4, S5):** `http://<IP_LAN_EQUIPO_2>:8501`
