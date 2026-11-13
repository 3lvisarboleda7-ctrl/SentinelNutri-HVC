# Hoja de Ruta y Pendientes por Fase: Equipo 1 vs. Equipo 2 — SentinelNutri-HVC

**Proyecto:** SentinelNutri-HVC: Sistema Inteligente de Alerta Temprana para el Sistema 4 del MSV, Región Huancavelica  
**Curso:** Modelo de Sistema Viable (MSV) — FIIS UNI  
**Documento Base:** `Perfil_Msv_Huancavelica_APA7 (5).docx`

---

## Resumen de Roles de Infraestructura (Tabla 3 del Proyecto)

| Etiqueta | Equipo / Entorno | Hardware y Sistema Operativo | Rol Principal en la Arquitectura |
| :--- | :--- | :--- | :--- |
| **`[EQUIPO 1]`** | **Estación de Desarrollo** | Intel Core i7-1355U · 16 GB RAM · SSD 477 GB · **Windows 11 Pro** | Desarrollo en VS Code, programación de scrapers/API/Dashboard, pruebas (`pytest`), gestión de Git/GitHub y conexión por red local (LAN) hacia el Equipo 2. |
| **`[EQUIPO 1 -> COLAB]`** | **Google Colab (Nube Gratuita)** | Runtimes CPU / GPU T4 gratuitos de Google | Ejecución desde el navegador del **Equipo 1** del entrenamiento pesado de `CatBoost + SHAP`, validación cruzada estratificada ($\text{AUC} \ge 0,90$) y exportación de `.cbm` y gráficas para el informe. |
| **`[EQUIPO 2 - SSD]`** | **Servidor Local (Disco Sólido)** | Intel Core i7-7700HQ · 16 GB RAM · **SSD 447 GB (`C:\`)** · **Windows 10** | Aloja Docker Desktop y los contenedores activos de respuesta rápida: `PostgreSQL 16`, `n8n Community Edition`, `FastAPI + Playwright`, `Streamlit` y `cloudflared` (**Cloudflare Tunnel**). |
| **`[EQUIPO 2 - HDD + GPU]`** | **Servidor Local (Disco Duro + GPU)** | **HDD 1 TB (`D:\`)** + **GPU NVIDIA GTX 1050 (4 GB VRAM)** · **Windows 10** | **HDD (`D:\`):** Almacena archivos crudos descargados (`/raw`), respaldos de BD (`/backups`), modelos entrenados (`/models`) y pesos de LLM (`/ollama_models`).<br/>**GPU GTX 1050:** Acelera `Ollama` (`llama3.2`) como respaldo local gratuito. |

---

## Estado Global de Avance

- [x] **Cimientos de Arquitectura Clean / Hexagonal y Monorepo** (`[EQUIPO 1]` — **Completado**)
- [x] **Implementación de las 3 Reglas Fijas y Guardarraíl Ley N.º 29733** (`[EQUIPO 1]` — **Completado, blindado con Red-Team QA Fases 1–6 y testeado 22/22**)
- [x] **Esqueleto funcional de las 6 Herramientas del Agente Supervisor en FastAPI** (`[EQUIPO 1]` — **Completado**)
- [x] **Catálogo de 100 distritos + 6 Scrapers + Exportación CSV/JSON y 4 Figuras XAI (300 DPI)** (`[EQUIPO 1]` — **Completado**)
- [x] **Fase 3 (Semana 4): Ejecución de los 3 notebooks en Google Colab y modelo `.cbm` integrado** (`[EQUIPO 1 -> COLAB]` — **Completado**)
- [x] **Fase 1 y 2 (Semanas 2–3):** Aprovisionamiento del servidor local (`[EQUIPO 2]`: SSD + HDD 1 TB + Ollama GTX 1050 + PostgreSQL 16 + Backfill 1 100 registros — **Completado**).
- [x] **Fase 4 (Semana 5):** `n8n` (`:5678`) desplegado con cuenta `3lvisarboleda7@gmail.com`, 2 workflows importados (`ofxz76BJS918zdeq` y `27ZPF1SbAx1tCSxv`), credenciales Gemini y Telegram activadas y operativas en vivo (`[EQUIPO 2]` — **Completado al 100%**).
- [x] **Fase 5 (Semana 6):** Dashboard Streamlit (`:8501`) y API FastAPI (`:8000`) 100% encapsulados en Docker Compose con persistencia tras reinicios, respaldo SQL SSD $\rightarrow$ HDD (`2,18 MB`), gráficos interactivos y HITL S3 validado por API (`[EQUIPO 2]` — **Completado al 100%**).
- [x] **Fase 6 (Semana 7):** Integración de capturas en vivo del Equipo 2 (`docs/figures/equipo2_live_01_*.png` a `06_*.png`) al informe final (`[EQUIPO 2]` — **Completado**).

---

## Detalle de Pendientes por Fase y por Equipo

### FASE 1 (Semana 2 del Cronograma): Entorno de Costo Cero e Infraestructura Dual

#### En el `[EQUIPO 1 · Estación de Desarrollo (Windows 11)]`
- [x] Diseñar la arquitectura Clean/Hexagonal (`domain`, `application`, `infrastructure`, `interfaces`).
- [x] Crear `deploy/docker-compose.equipo2.yml` separando volúmenes SSD (`C:\`) y HDD (`D:\`).
- [x] Crear los scripts PowerShell de aprovisionamiento para el Equipo 2 en `deploy/scripts_equipo2/`.
- [x] Implementar detector automático de máquina (`python -m sentinelnutri.cli whoami` en `src/sentinelnutri/config/node_detector.py`) por huella de hardware/SO (`i7-1355U` vs `i7-7700HQ` + `GTX 1050`).
- [x] Inicializar el repositorio Git local (`git init` + commits en rama `main`).
- [x] Subir el repositorio local a **GitHub** (`https://github.com/3lvisarboleda7-ctrl/SentinelNutri-HVC`) para clonarlo desde el Equipo 2 y abrir los notebooks directamente en Google Colab.
- [ ] Colocar la IP LAN del Equipo 2 en `config/.env.equipo1` del Equipo 1 (`EQUIPO2_LAN_IP=10.36.113.176`, detectada el 2026-11-10; es DHCP, verificar con `ipconfig` en el Equipo 2 si cambia). *El archivo vive solo en el Equipo 1 (gitignored).*

#### En el `[EQUIPO 2 · Servidor Local (Windows 10 · SSD + HDD 1 TB · GTX 1050)]`
- [x] Clonar el repositorio de GitHub en el Equipo 2 (`D:\3lvix\SentinelNutri-HVC`).
- [x] Ejecutar en PowerShell el script `.\deploy\scripts_equipo2\01_setup_ssd_hdd_dirs.ps1` para crear automáticamente:
  - En el **SSD (`C:\SentinelNutri\ssd\`)**: `postgres_data` y `n8n_data`.
  - En el **HDD de 1 TB (`D:\SentinelNutri\hdd\`)**: `raw`, `models`, `backups`, `ollama_models` y `diresa_convenio_ley29733`.
- [x] Ejecutar el script `.\deploy\scripts_equipo2\02_install_ollama_gpu.ps1` en el Equipo 2 para:
  - Verificar que `nvidia-smi` detecte la tarjeta **NVIDIA GTX 1050 (4 GB VRAM, Driver 566.36, CUDA 12.7)**.
  - Instalar **Ollama (`v0.40.16`)** en Windows 10.
  - Fijar `OLLAMA_MODELS=D:\SentinelNutri\hdd\ollama_models` (para que los modelos se guarden en el disco duro de 1 TB y no ocupen el SSD).
  - Fijar `OLLAMA_HOST=0.0.0.0:11434` y descargar el modelo `llama3.2`.
- [x] Copiar `config/.env.equipo2.example` a `config/.env.equipo2` y levantar la base de datos `sentinelnutri_postgres` (`postgres:16-alpine`) y el motor REST `FastAPI` (`:8000`) en el Equipo 2:
  ```powershell
  docker compose -p sentinelnutri -f deploy/docker-compose.equipo2.yml --env-file config/.env.equipo2 up -d postgres n8n
  ```

---

### FASE 2 (Semana 3 del Cronograma): Extracción Automatizada (Web Scraping) y Preprocesamiento

#### En el `[EQUIPO 1 · Estación de Desarrollo (Windows 11)]`
- [x] **Catálogo completo de Ubigeos:** Ampliado tanto en `src/sentinelnutri/infrastructure/persistence/database.py` como en `database/migrations/V2__seed_ubigeos_huancavelica.sql` y `huancavelica_distritos.geojson` a los **100 distritos oficiales de las 7 provincias de Huancavelica** (`090101` al `090721`, integrando `1 100` registros históricos 2014–2024).
- [x] **Scraper 1 — SIEN-HIS (INS/CENAN) y Datos Abiertos (`sien_ins_scraper.py`):**
  - Programado con soporte para CSV/XLSX de Datos Abiertos y extracción de tablas en PDF con `PyMuPDF` (`fitz`) / `pdfplumber` y armonización automática de `ubigeo`.
- [x] **Scraper 2 — ENDES INEI (`endes_inei_scraper.py`):**
  - Programado con lectura de microdatos `.sav` (`pyreadstat`) y tablas CSV filtrando el departamento `09 (Huancavelica)` (agua con cloro adecuado, saneamiento, educación materna, lactancia y controles CRED).
- [x] **Scraper 3 — INEI Censos y Mapa de Pobreza (`inei_pobreza_scraper.py`):**
  - Programada la ingesta distrital de pobreza monetaria, ruralidad y población menor de 5 años.
- [x] **Scraper 4 — MEF Consulta Amigable con Playwright (`mef_pan_playwright.py`):**
  - Programada la navegación `Playwright` y parser de tablas HTML para el Departamento `09: HUANCAVELICA` y Categoría Presupuestal `0001: PROGRAMA ARTICULADO NUTRICIONAL` (PIM, Devengado y % de Ejecución 2014–2024).
- [x] **Scraper 5 — MIDIS con Playwright (`midis_playwright.py`):**
  - Programada la extracción en REDinforma / InfoMIDIS de la cobertura distrital de **Juntos**, **Cuna Más** y **Qali Warma**.
- [x] **Scraper 6 — SENAMHI (`senamhi_scraper.py`):**
  - Programada la extracción e interpolación por gradiente altitudinal andino de días de heladas, temperatura mínima y precipitación para los 100 distritos.
- [x] Ejecutar las 22 pruebas unitarias, adversariales Red-Team Fases 1–6 (`tests/unit/test_adversarial_red_team.py`) e integración E2E (`python tests/run_all_tests.py` $\rightarrow$ **22/22 PASS**).

#### En el `[EQUIPO 2 · Servidor Local (Windows 10 · SSD + HDD 1 TB)]`
- [x] Actualizar los scrapers y el adaptador dual `psycopg2` (`database.py` + `postgres_repo.py`) y levantar el motor `api_engine` (`:8000`).
- [x] Disparar la primera ejecución masiva en modo **`backfill` (2014–2024)** sobre PostgreSQL 16 (`sentinelnutri_postgres`):
  ```powershell
  $env:PYTHONPATH="src;."; $env:DATABASE_URL="postgresql+psycopg2://sentinel_user:sentinel_pass_2026@localhost:5432/sentinelnutri_hvc"; .\.venv\Scripts\python -m sentinelnutri.cli bootstrap --env prod
  ```
- [x] Verificar que todos los archivos crudos descargados (`endes_inei`, `inei_pobreza`, `mef_pan`, `midis_programas`, `senamhi_clima`, `sien_his`) hayan quedado guardados en el **HDD de 1 TB (`D:\SentinelNutri\hdd\raw\`)** y que las tablas `serie_historica_distrital` (`1 100` filas), `predicciones_dci` (`100` filas) y `registro_cargas` en el **PostgreSQL del SSD** tengan las fechas y huellas digitales `SHA-256`.

---

### FASE 3 (Semana 4 del Cronograma): Motor Predictivo CatBoost + SHAP (XAI)

#### En el `[EQUIPO 1 -> GOOGLE COLAB (Entrenamiento Pesado en la Nube)]`
- [x] Exportar el dataset histórico consolidado `2014–2024` a [`data/exports/panel_distrital_hvc_2014_2024.csv`](file:///c:/Users/arbol/OneDrive/Univesidad_Nacional_de_Ingenieria/Ciclo_8/MSV/SentinelNutri-HVC/data/exports/panel_distrital_hvc_2014_2024.csv) (`1 100` filas × 24 columnas) mediante `python -m sentinelnutri.cli export-artifacts`.
- [x] Preparar los 3 notebooks completos en `notebooks_colab/` (`01_backfill_y_exploracion_sien_2014_2024.ipynb`, `02_entrenamiento_catboost_shap_colab.ipynb`, `03_evaluacion_xai_y_gobernanza.ipynb`).
- [x] Ejecutar `02_entrenamiento_catboost_shap_colab.ipynb` en **Google Colab** y descargar `catboost_dci_hvc.cbm` (`364 KB`, integrado en [`data/models/catboost_dci_hvc.cbm`](file:///c:/Users/arbol/OneDrive/Univesidad_Nacional_de_Ingenieria/Ciclo_8/MSV/SentinelNutri-HVC/data/models/catboost_dci_hvc.cbm)) junto con las 3 gráficas de SHAP/ROC de Colab en `docs/figures/colab_*.png`.

#### En el `[EQUIPO 2 · Servidor Local (Windows 10 · HDD 1 TB + SSD)]`
- [x] Copiar el modelo entrenado `catboost_dci_hvc.cbm` hacia la carpeta del **HDD de 1 TB del Equipo 2**: `D:\SentinelNutri\hdd\models\`.
- [x] Verificar que el endpoint `POST http://localhost:8000/predict` y `GET http://localhost:8000/tools/explicar_riesgo/090411` carguen el modelo del HDD y devuelvan las predicciones (`Santa Ana 29,29 % -> CRITICO -> S5_ALGEDONICO`) y valores SHAP en menos de 1 segundo.

---

### FASE 4 (Semana 5 del Cronograma): Módulo Agéntico en n8n, 6 Herramientas y Reglas Fijas

#### En el `[EQUIPO 1 · Estación de Desarrollo (Windows 11)]`
- [ ] Obtener las credenciales gratuitas de los servicios externos:
  1. **Google AI Studio:** Crear API Key gratuita de **Gemini** (`GEMINI_API_KEY`).
  2. **Telegram (`@BotFather`):** Crear el bot `@SentinelNutriHVC_Bot`, obtener `TELEGRAM_BOT_TOKEN` y los `CHAT_ID` para el **Consejo Regional (S5)**, la **Gerencia Regional de Desarrollo Social (S3)** y **Alertas Técnicas de Fallos de Scraper**.
  3. **Gmail:** Crear una *Contraseña de Aplicación* (`GMAIL_APP_PASSWORD`) en la cuenta de Google del proyecto.
- [x] Vincular credenciales en los workflows: `Ollama Local GPU GTX 1050 (Equipo 2)`, `Google Gemini Free Tier (AI Studio)` y `Telegram Bot SentinelNutri-HVC (S5/S3)` ya asignadas a sus nodos (Gemini y Telegram con valor de relleno hasta recibir las claves reales).

#### En el `[EQUIPO 2 · Servidor Local (Windows 10 · SSD + GPU GTX 1050)]`
- [x] Configurar `config/.env.equipo2` y dejar listos los conectores para `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN` y `GMAIL_APP_PASSWORD` (con simulación segura por defecto).
- [x] Levantar el contenedor de `n8n` (`sentinelnutri_n8n_supervisor`) en el SSD del Equipo 2:
  ```powershell
  docker compose -p sentinelnutri -f deploy/docker-compose.equipo2.yml --env-file config/.env.equipo2 up -d --no-deps n8n
  ```
- [x] Importar en `n8n` (`http://localhost:5678`) los 2 flujos de `workflows_n8n/`:
  1. `01_ciclo_supervisor_sentinelnutri.json` (`ofxz76BJS918zdeq`: Agente Supervisor con sus **6 herramientas** + **Regla Fija 1** `Schedule Trigger` + **Regla Fija 2** `Nodo IF DCI > 25% -> S5` + **Regla Fija 3** `Aprobación Humana Telegram/Gmail -> S3`).
  2. `02_vigilancia_fallos_scrapers.json` (`27ZPF1SbAx1tCSxv`: Autodiagnóstico por Telegram cuando un portal cambia de diseño).
- [x] Probar y blindar la conmutación automática del `llm_gateway.py`: **Ruta A (`Gemini Free Tier`)** $\rightarrow$ **Ruta B (`Ollama llama3.2` acelerado por GPU GTX 1050)** $\rightarrow$ **Ruta C (`Motor Estructurado MSV`)** (`0,18 ms` de failover).

---

### FASE 5 (Semana 6 del Cronograma): Cloudflare Tunnel, Aprobación desde Celular y Dashboard Streamlit

#### En el `[EQUIPO 2 · Servidor Local (Windows 10 · SSD)]`
- [ ] *(Opcional cuando se tenga dominio propio)* Crear el túnel gratuito en **Cloudflare Zero Trust** (`Networks -> Tunnels`), copiar el token en `config/.env.equipo2` (`CLOUDFLARE_TUNNEL_TOKEN`) y apuntar el subdominio HTTPS hacia `http://n8n:5678`.
- [x] Levantar el Dashboard Cibernético Streamlit (`:8501`) conectado a `sentinelnutri_postgres` y FastAPI (`:8000`).
- [x] Ejecutar y validar el script `.\deploy\scripts_equipo2\04_backup_postgres_to_hdd.ps1` volcando una copia de seguridad completa de PostgreSQL (`2,18 MB`) en el **HDD de 1 TB (`D:\SentinelNutri\hdd\backups\`)**.

#### En `[AMBOS EQUIPOS + Celular (Pruebas de Canales MSV)]`
- [x] **Prueba del Canal Algedónico Automatizado (S1/S4 $\rightarrow$ S5):** Verificado en vivo sobre PostgreSQL 16 con el distrito **`Santa Ana 090411`** (`DCI proyectada = 29,29 % > 25,0 %`), disparando de inmediato la alerta algedónica con estado `ALGEDONICO_DIRECTO_S5` hacia el Consejo Regional (S5) sin esperar aprobación humana.
- [x] **Prueba del Canal de Control con Aprobación Humana (S4 $\rightarrow$ S3):** Verificado en vivo con el distrito **`Huancavelica 090101`** (`DCI proyectada = 7,82 % <= 25,0 %`): bloqueado inicialmente en `PENDIENTE_APROBACION` (`publicado_en_canal_control_s3: false`) y desbloqueado vía `POST /hitl/aprobar/2` pasando a `APROBADO_S3` (`publicado_en_canal_control_s3: true`).

---

### FASE 6 (Semana 7 del Cronograma): Evaluación XAI, Gobernanza y Documentación Final

#### En el `[EQUIPO 1 · Estación de Desarrollo (Windows 11)]`
- [x] Generar automáticamente en el Equipo 1 las tablas, reportes y 4 figuras de `300 DPI` para los **Capítulos 5, 6 y 7 del Informe Final** (`python -m sentinelnutri.cli export-artifacts`):
  - Reporte de métricas ($\text{AUC-ROC} = 0,9993 \ge 0,90$, $\text{F1} = 0,8917$, exactitud por las 7 provincias): [`data/exports/metrics_report.json`](file:///c:/Users/arbol/OneDrive/Univesidad_Nacional_de_Ingenieria/Ciclo_8/MSV/SentinelNutri-HVC/data/exports/metrics_report.json).
  - Matriz completa de gobernanza para los 100 distritos (Canal Algedónico S5 vs Control S3, factor SHAP principal, recomendaciones Salud/Agua/Agricultura, **OEI PEI 2020–2027** y **ODS 2, 3 y 6**): [`data/exports/matriz_gobernanza_oei_ods_hvc.csv`](file:///c:/Users/arbol/OneDrive/Univesidad_Nacional_de_Ingenieria/Ciclo_8/MSV/SentinelNutri-HVC/data/exports/matriz_gobernanza_oei_ods_hvc.csv).
  - 4 Figuras académicas en `300 DPI` listas para insertar en Word:
    1. [`docs/figures/fig1_roc_cv5_catboost_hvc.png`](file:///c:/Users/arbol/OneDrive/Univesidad_Nacional_de_Ingenieria/Ciclo_8/MSV/SentinelNutri-HVC/docs/figures/fig1_roc_cv5_catboost_hvc.png)
    2. [`docs/figures/fig2_shap_importancia_global_s3_star.png`](file:///c:/Users/arbol/OneDrive/Univesidad_Nacional_de_Ingenieria/Ciclo_8/MSV/SentinelNutri-HVC/docs/figures/fig2_shap_importancia_global_s3_star.png)
    3. [`docs/figures/fig3_shap_waterfall_distrito_critico.png`](file:///c:/Users/arbol/OneDrive/Univesidad_Nacional_de_Ingenieria/Ciclo_8/MSV/SentinelNutri-HVC/docs/figures/fig3_shap_waterfall_distrito_critico.png)
    4. [`docs/figures/fig4_homeostato_s3_s4_7_provincias.png`](file:///c:/Users/arbol/OneDrive/Univesidad_Nacional_de_Ingenieria/Ciclo_8/MSV/SentinelNutri-HVC/docs/figures/fig4_homeostato_s3_s4_7_provincias.png)
- [x] Tomar las 7 capturas de pantalla en alta resolución (`docs/figures/equipo2_live_01_*.png` a `07_*.png`) del Dashboard Streamlit (`:8501`), API FastAPI (`:8000/docs`) y orquestador `n8n` (`:5678`) en vivo en el **Equipo 2** e integrarlas en [`docs/CAPITULOS_5_6_7_INFORME_FINAL_APA7.md`](docs/CAPITULOS_5_6_7_INFORME_FINAL_APA7.md).
- [x] Ejecutar el ensayo End-to-End en vivo sobre LAN (`Equipo 1 -> Equipo 2 192.168.1.6`, `53,94 s`) con `gemini-flash-lite-latest` real y actualizar [`docs/CAPITULOS_5_6_7_INFORME_FINAL_APA7.md`](docs/CAPITULOS_5_6_7_INFORME_FINAL_APA7.md) con el sustento empírico y estadístico de los indicadores actuales (`2014–2024`, $N=1\,100$).
- [ ] *(Próxima semana)* Evaluar e integrar la aplicación de los **indicadores sistémicos de Parra Luna** sobre el panel consolidado de Huancavelica y actualizar la sección correspondiente del informe.

