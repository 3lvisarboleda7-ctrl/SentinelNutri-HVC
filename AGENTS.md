# Memoria Permanente del Proyecto — SentinelNutri-HVC (`AGENTS.md`)

Este archivo es leído automáticamente por Antigravity en cada sesión y turno dentro de este repositorio. Funciona como **índice maestro y memoria persistente** del proyecto **SentinelNutri-HVC: Sistema Inteligente de Alerta Temprana para el Sistema 4 del MSV, Región Huancavelica** (Curso: Modelo de Sistema Viable — FIIS UNI, Prof. Ricardo Rodríguez-Ulloa, Autor: Elvis Arboleda).

> **Regla de Mantenimiento de Memoria:** Cada vez que se cree, mueva o modifique un componente importante o se complete una tarea de una fase, el agente DEBE actualizar este archivo (`AGENTS.md`) y el archivo `PENDIENTES_POR_FASE_EQUIPOS.md`.

---

## 1. Mapa de Documentos Base del Proyecto (Fuera y Dentro del Repo)

### A. Documentos Académicos y de Caso en la PC del Usuario (`Equipo 1`)
- **Perfil Final del Proyecto (Versión 5 APA 7 con Equipo 1/Equipo 2, Agente Supervisor, 6 Herramientas y 3 Reglas Fijas):**
  - `C:\Users\arbol\Downloads\Perfil_Msv_Huancavelica_APA7 (5).docx`
- **Resumen General del Caso Huancavelica 2000–2040 (SSM, SSDM, 11 OEI del PEI 2020-2027, Arquetipos, ODS y MSV):**
  - `C:\Users\arbol\Downloads\Proyecto_MSV_Resumen.md`
- **PEI GORE Huancavelica Ampliado 2020–2027 (RER N° 089-2024):**
  - `C:\Users\arbol\Downloads\PEI_GORE_Huancavelica_2020-2027_Ampliado.pdf`
- **Paper de Referencia XAI (CatBoost + SHAP en SIEN Perú, Meta $\text{AUC} \ge 0,90$):**
  - `C:\Users\arbol\Downloads\4.An Explainable Artificial Intelligence Framework for Chronic Malnutrition Surveillance in...` (Navarro-Guillén et al., 2026)
- **Libros y Sílabo del Curso MSV (Carpeta Padre):**
  - `C:\Users\arbol\OneDrive\Univesidad_Nacional_de_Ingenieria\Ciclo_8\MSV\msv-silabo.pdf`
  - `C:\Users\arbol\OneDrive\Univesidad_Nacional_de_Ingenieria\Ciclo_8\MSV\Brain of the Firm - Stafford Beer.pdf`

### B. Documentos de Gestión y Planificación Dentro del Repositorio
- **Repositorio Remoto Oficial en GitHub:** `https://github.com/3lvisarboleda7-ctrl/SentinelNutri-HVC`
- `README.md`: Visión general, arquitectura híbrida y comandos rápidos para Equipo 1 y Equipo 2.
- `PENDIENTES_POR_FASE_EQUIPOS.md`: Checklist detallado por fases (Semanas 2 a 7) separado por `[EQUIPO 1]`, `[EQUIPO 1 -> COLAB]` y `[EQUIPO 2]`.
- `docs/CAPITULOS_5_6_7_INFORME_FINAL_APA7.md`: Redacción académica completa en formato APA 7 de los Capítulos 5, 6 y 7 con tablas de métricas, valores SHAP, distritos críticos S5 y alineación PEI/ODS.
- `docs/GUIA_PASO_A_PASO_EQUIPO1_Y_EQUIPO2.md`: Guía operativa con enlaces directos a Google Colab y comandos para Equipo 2.

---

## 2. Infraestructura Dual de Costo Cero y Detección Automática de Nodo (Tabla 3)

> **Regla de Detección Automática (Equipo 1 vs Equipo 2):** Como la carpeta del proyecto puede sincronizarse por **OneDrive** o clonarse por **Git** entre ambas computadoras, Antigravity y el código Python detectan automáticamente en qué máquina están corriendo mediante [`src/sentinelnutri/config/node_detector.py`](file:///c:/Users/arbol/OneDrive/Univesidad_Nacional_de_Ingenieria/Ciclo_8/MSV/SentinelNutri-HVC/src/sentinelnutri/config/node_detector.py) y el comando:
> ```powershell
> $env:PYTHONPATH="src;."; python -m sentinelnutri.cli whoami
> ```
> - Si detecta `Hostname=ELVIS` o CPU `i7-1355U` o `Windows 11 Pro` $\rightarrow$ **`EQUIPO_1` (Estación de Desarrollo)**.
> - Si detecta CPU `i7-7700HQ` o GPU `NVIDIA GTX 1050` o `D:\SentinelNutri\hdd` $\rightarrow$ **`EQUIPO_2` (Servidor Local)**.
> - También se puede forzar localmente creando un archivo `.node_override` (ignorado por Git) con el texto `EQUIPO_1` o `EQUIPO_2`.

1. **Equipo 1 — Estación de Desarrollo (Hostname: `ELVIS`):**
   - **Hardware/SO:** Intel Core i7-1355U · 16 GB RAM · SSD 477 GB · Windows 11 Pro.
   - **Rol:** Desarrollo en VS Code, pruebas (`python tests/run_all_tests.py`), ejecución de notebooks pesados en **Google Colab** y acceso por red local (LAN) a `n8n` (`:5678`) y `Streamlit` (`:8501`) del Equipo 2.
2. **Equipo 2 — Servidor Local:**
   - **Hardware/SO:** Intel Core i7-7700HQ · 16 GB RAM · **GPU NVIDIA GTX 1050 (4 GB VRAM)** · **SSD 447 GB (`C:\`)** + **HDD 1 TB (`D:\`)** · Windows 10.
   - **En SSD (`C:\SentinelNutri\ssd\`):** Contenedores Docker rápidos (`postgres`, `api_engine` con FastAPI+Playwright, `n8n`, `dashboard` Streamlit, `cloudflared`).
   - **En HDD (`D:\SentinelNutri\hdd\`):** Archivos crudos descargados (`/raw`), modelos entrenados (`/models/catboost_dci_hvc.cbm`), respaldos de BD (`/backups`) y pesos de Ollama (`/ollama_models`).
   - **GPU GTX 1050 (4 GB):** Ejecuta **Ollama (`llama3.2`)** nativo en Windows 10 como LLM de respaldo local (`http://host.docker.internal:11434`).
   - **Cloudflare Tunnel (`cloudflared`):** Publica `n8n` con HTTPS seguro sin abrir puertos del router, permitiendo aprobar recomendaciones desde el celular y protegiendo Windows 10.

---

## 3. Índice Exacto de Archivos de Código (Dónde Está Cada Cosa)

### Capa 1: Dominio Cibernético y Reglas Fijas (`src/sentinelnutri/domain/`)
- **Entidades MSV (`domain/entities/`):**
  - `district.py`: `DistrictMetadata` y `DistrictIndicatorRecord` (las 5 dimensiones por `ubigeo`).
  - `prediction.py`: `DistrictRiskPrediction`, `RiskLevel` y `ShapContribution`.
  - `alert_msv.py`: `MSVAlertReport`, `MSVChannel` (`S3_CONTROL`, `S5_ALGEDONICO`) y `ApprovalStatus`.
- **Las 3 Reglas Fijas, Privacidad y Ética (`domain/rules/`):**
  - `fixed_thresholds.py`:
    - **Regla Fija 1:** El riesgo numérico lo calcula siempre `CatBoost`, nunca el LLM.
    - **Regla Fija 2 (`evaluate_fixed_algedonic_rule`):** Si `DCI proyectada > 25,0 %`, activa **siempre** el **Canal Algedónico hacia S5 (Consejo Regional)**.
    - **Regla Fija 3 (`can_publish_to_s3_control`):** Requiere estado `APROBADO_S3` (aprobación humana por Telegram/Gmail) antes de publicar en el **Canal de Control S3 (GRDS)**.
  - `privacy_guard.py`: Guardarraíl **Ley N.º 29733** (`sanitize_district_payload_for_llm`); bloquea cualquier campo nominal (`dni`, `nombres`, `historia_clinica`, etc.) antes de llamar al LLM.
  - `scraping_ethics.py`: Verificador de `robots.txt`, validación de `User-Agent` académico FIIS-UNI y cálculo de huella digital `SHA-256` (`compute_sha256_hash`, `has_file_changed`).
- **Puertos Hexagonales (`domain/ports/`):**
  - `repository_port.py`, `scraper_port.py`, `predictor_port.py`.

### Capa 2: Aplicación — Las 6 Herramientas del Agente Supervisor (`src/sentinelnutri/application/`)
Mapeadas 1 a 1 con la **Tabla 5** del documento de perfil:
1. `tool_1_extraer_fuentes.py` (`Tool1ExtraerFuentesUseCase`): Ejecuta scraping en modo `backfill` (2014–2024) o `weekly_watch` (vigilancia semanal comparando hash `SHA-256`).
2. `tool_2_consultar_bd.py` (`Tool2ConsultarBdUseCase`): Lee series históricas 2014–2024 de los 100 distritos de Huancavelica.
3. `tool_3_predecir_riesgo.py` (`Tool3PredecirRiesgoUseCase`): Ejecuta inferencia de riesgo distrital y aplica la Regla Fija Algedónica (`> 25 % -> S5`).
4. `tool_4_explicar_riesgo.py` (`Tool4ExplicarRiesgoUseCase`): Calcula contribuciones locales **SHAP** por variable para la auditoría **S3***.
5. `tool_5_redactar_informe.py` (`Tool5RedactarInformeUseCase`): Verifica **Ley N.º 29733** y genera síntesis narrativa **S4** + recomendaciones por sector (**Salud/DIRESA**, **Agua/DRVCS**, **Agricultura/MIDIS/MEF**) alineadas a los **OEI del PEI 2020–2027** y **ODS 2, 3 y 6**.
6. `tool_6_notificar.py` (`Tool6NotificarUseCase`): Enruta señales algedónicas directas al **S5** por Telegram/Gmail y gestiona la espera de aprobación humana (`HITL`) para el **S3**.

### Capa 3: Infraestructura (`src/sentinelnutri/infrastructure/`)
- **Persistencia (`infrastructure/persistence/`):**
  - `database.py`: Inicializador dual SQLite (Equipo 1) / PostgreSQL (Equipo 2) con la semilla de los **100 distritos oficiales de las 7 provincias de Huancavelica** (`DEFAULT_HUANCAVELICA_DISTRICTS`).
  - `postgres_repo.py`: Implementación completa de `RepositoryPort` (`SqlAlchemyRepository`).
  - `models_orm.py`: Declaración ORM de las 5 tablas (`cat_ubigeo_hvc`, `registro_cargas`, `serie_historica_distrital`, `predicciones_dci`, `alertas_y_recomendaciones_msv`).
- **Scrapers Automatizados (`infrastructure/scrapers/` — Tabla 4 del Proyecto):**
  - `base_ethical_scraper.py`: Cliente HTTP y `Playwright` con validación `robots.txt`, rate-limit y guardado en HDD con `SHA-256`.
  - `multi_source_orchestrator.py`: Orquesta las 6 fuentes (`SIEN_HIS`, `ENDES_INEI`, `INEI_POBREZA`, `MEF_PAN`, `MIDIS_PROGRAMAS`, `SENAMHI_CLIMA`) e integra las `1 100` filas (100 distritos × 11 años).
  - Módulos específicos por portal: `sien_ins_scraper.py`, `endes_inei_scraper.py`, `inei_pobreza_scraper.py`, `mef_pan_playwright.py`, `midis_playwright.py`, `senamhi_scraper.py`, `diresa_folder_watcher.py`.
- **ETL (`infrastructure/etl/`):** `ubigeo_harmonizer.py` y `feature_pipeline.py`.
- **Motor Predictivo XAI (`infrastructure/ml_xai/`):**
  - `catboost_shap_predictor.py`: Motor `CatBoost + SHAP` con validación cruzada estratificada ($\text{AUC-ROC} = 0,9993 \ge 0,90$, $\text{F1} = 0,8917$).
  - `catboost_adapter.py` (carga de `.cbm` desde HDD) y `shap_adapter.py` (formato S3*).
- **Notificaciones y LLM (`infrastructure/notifications/`):**
  - `llm_gateway.py`: Conector agnóstico **Gemini Free Tier (Google AI Studio)** con fallback automático a **Ollama (`llama3.2` en GTX 1050)**.
  - `telegram_gmail_clients.py`: Clientes de notificación para Telegram Bot API y Gmail SMTP.

### Capa 4: Interfaces, Workflows n8n, Colab y Despliegue
- **API FastAPI (`src/sentinelnutri/interfaces/api/main.py`):**
  - Endpoints: `/health`, `/predict`, `/tools/extraer_fuentes`, `/tools/consultar_bd`, `/tools/predecir_riesgo`, `/tools/explicar_riesgo/{ubigeo}`, `/tools/redactar_informe`, `/tools/notificar`, `/hitl/aprobar/{alert_id}`, `/evaluation/metrics`.
- **Dashboard Streamlit (`src/sentinelnutri/interfaces/dashboard/`):**
  - `app.py` y multipágina en `pages/`: `01_S4_S3_Homeostato.py`, `02_S3_Star_Auditoria_SHAP.py`, `03_S2_Coordinacion_Redes.py`, `04_S5_Canal_Algedonico_ODS.py`.
- **Flujos n8n (`workflows_n8n/`):**
  - `01_ciclo_supervisor_sentinelnutri.json` y `02_vigilancia_fallos_scrapers.json` + prompts en `workflows_n8n/prompts/`.
- **Notebooks para Google Colab (`notebooks_colab/`):**
  - `01_backfill_y_exploracion_sien_2014_2024.ipynb`
  - `02_entrenamiento_catboost_shap_colab.ipynb` (listo para entrenar CatBoost+SHAP en Colab y descargar `catboost_dci_hvc.cbm` + gráficos PNG de 300 DPI).
  - `03_evaluacion_xai_y_gobernanza.ipynb`
- **Infraestructura Equipo 2 (`deploy/` y `database/`):**
  - `deploy/docker-compose.equipo2.yml` y scripts PowerShell en `deploy/scripts_equipo2/` (`01_setup_ssd_hdd_dirs.ps1`, `02_install_ollama_gpu.ps1`, `03_setup_cloudflare_tunnel.ps1`, `04_backup_postgres_to_hdd.ps1`).
  - Migraciones SQL en `database/migrations/` (`V1__init_msv_schema.sql`, `V2__seed_ubigeos_huancavelica.sql`) y vistas en `database/queries/msv_views.sql`.

---

## 4. Artefactos Exportados, Dataset para Google Colab y Figuras de 300 DPI (`data/exports/` y `docs/figures/`)
Generados automáticamente por [`src/sentinelnutri/application/export_artifacts_service.py`](file:///c:/Users/arbol/OneDrive/Univesidad_Nacional_de_Ingenieria/Ciclo_8/MSV/SentinelNutri-HVC/src/sentinelnutri/application/export_artifacts_service.py):
- `data/exports/panel_distrital_hvc_2014_2024.csv`: Panel histórico consolidado de `1 100` registros (100 distritos × 11 años × 24 columnas), listo para subir a Google Colab.
- `data/exports/metrics_report.json`: Reporte completo de validación ($\text{AUC-ROC} = 0,9993 \ge 0,90$, $\text{F1} = 0,8917$, matriz de confusión, importancia global SHAP y resumen de las 7 provincias S2).
- `data/exports/matriz_gobernanza_oei_ods_hvc.csv`: Matriz de los 100 distritos con proyección DCI, canal MSV (`S5_ALGEDONICO` vs `S3_CONTROL`), factor SHAP principal, recomendaciones sectoriales (Salud, Agua, Agricultura) y vinculación con los **OEI del PEI 2020–2027** y **ODS 2, 3 y 6**.
- `docs/figures/`: 4 figuras académicas en `300 DPI` listas para los Capítulos 5, 6 y 7 del informe:
  - `fig1_roc_cv5_catboost_hvc.png`
  - `fig2_shap_importancia_global_s3_star.png`
  - `fig3_shap_waterfall_distrito_critico.png`
  - `fig4_homeostato_s3_s4_7_provincias.png`

---

## 5. Estado Operativo Real del Equipo 2 (Servidor Local) — Mantener Siempre Actualizado

> **Regla:** Esta sección refleja el estado *real* verificado, no el deseado. Si algo no se probó en vivo, se marca como pendiente.

- **Host detectado:** `DESKTOP-H3C8P9R` · i7-7700HQ · GTX 1050 4 GB (Driver 566.36) · Windows 10 Home · Repo en `D:\3lvix\SentinelNutri-HVC` · `.venv` con CPython 3.12 (`uv`).
- **IP LAN del Equipo 2:** `10.36.113.176` (asignada por DHCP: verificar con `ipconfig` si cambia de red). Desde el Equipo 1: `http://10.36.113.176:5678` (n8n), `:8501` (Streamlit), `:8000/docs` (API).
- **Proyecto Docker aislado:** `-p sentinelnutri` con `deploy/docker-compose.equipo2.yml` + `config/.env.equipo2` (gitignored). Los 4 contenedores están activos y encapsulados en Docker: `sentinelnutri_postgres` (`:5432`), `sentinelnutri_api_engine` (`:8000`), `sentinelnutri_streamlit_msv` (`:8501`) y `sentinelnutri_n8n_supervisor` (`:5678`). **No tocar** contenedores ajenos (p. ej. `contextapp-fase1-*`).
- **Ollama:** `v0.40.16` con `OLLAMA_VULKAN=1` y `CUDA_VISIBLE_DEVICES=-1` (el backend CUDA falla con el driver 566.36; Vulkan usa la GTX 1050). Modelos en `D:\SentinelNutri\hdd\ollama_models` (`llama3.2` Q4_K_M). Arranque automático al iniciar sesión configurado en Windows Startup (`SentinelNutri_Ollama_GPU.vbs`).
- **n8n (`sentinelnutri_n8n_supervisor`, v2.47.3):** propietario `3lvisarboleda7@gmail.com`. Workflows `ofxz76BJS918zdeq` (Ciclo Supervisor, 15 nodos con Ollama GTX 1050 nativo como chatModel del AI Agent) y `27ZPF1SbAx1tCSxv` (Vigilancia de scrapers). Credenciales: `Ollama Local GPU GTX 1050` (operativa en vivo), `Google Gemini Free Tier` y `Telegram Bot` (con valores de relleno, faltan claves reales). Variables: `N8N_SECURE_COOKIE=false` (login por LAN) y `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` (los nodos leen `$env.TELEGRAM_CHAT_ID_*`).
- **Regla Fija 3 en n8n (crítica):** el nodo `rule-fixed-3-human-approval` debe usar `sendAndWait`, sin `onError: continue`, seguido de la compuerta `¿Aprobado por Humano S3?` antes de `POST /hitl/aprobar/{id}`. Lo audita `test_red_team_6`.

### Registro de Cambios del Equipo 2
| Fecha | Commit | Cambio |
| :--- | :--- | :--- |
| 2026-11-10 | `7390e37` | PostgreSQL 16 dual (psycopg2), backfill 1 100 filas, Vulkan GTX 1050, suite Red-Team 22/22. |
| 2026-11-10 | `f646766` | CI: `streamlit` opcional en `app.py` para GitHub Actions. |
| 2026-11-10 | `d9bd783` | 6 capturas en vivo del Equipo 2 en el informe (sección 7.4). |
| 2026-11-10 | `be12c0b`, `f158994` | n8n: `api_engine -> host-gateway` y `N8N_SECURE_COOKIE=false`. |
| 2026-11-10 | `16b1aa4` | n8n: credenciales vinculadas a los nodos. **Introdujo una regresión en la Regla Fija 3** (HITL sin espera). |
| 2026-11-10 | `2cc1421` | Corrige la regresión: `sendAndWait` + compuerta de aprobación + test que lo audita. |
| 2026-11-10 | `48bd7f9` | docs(memoria): sincronización de estado operativo y pendientes honestos. |
| 2026-11-10 | En curso | Encapsulación de FastAPI y Streamlit dentro de Docker (`sentinelnutri_api_engine` y `sentinelnutri_streamlit_msv`), autostart de Ollama GPU en Windows y ejecución en vivo en n8n. |

### Pendientes Reales del Equipo 2
- [x] Contenedores Docker levantados y aislados (`postgres`, `api_engine`, `n8n`, `dashboard`).
- [x] Ollama GPU GTX 1050 operativo con autostart en Windows 10.
- [x] Workflows n8n operativos y conmutación LLM verificada.
- [x] Credenciales configuradas en vivo (`GEMINI_API_KEY` y `TELEGRAM_BOT_TOKEN`).
- [ ] Cloudflare Tunnel opcional (`CLOUDFLARE_TUNNEL_TOKEN`, para acceso fuera de la red local).

---

## 6. Comandos Clave de Verificación en Equipo 1
- Detectar automáticamente si estás en el Equipo 1 o en el Equipo 2:
  ```powershell
  $env:PYTHONPATH="src;."; python -m sentinelnutri.cli whoami
  ```
- Ejecutar bootstrap completo (Backfill 100 distritos 2014–2024 + Evaluación ML + Ciclo Supervisor):
  ```powershell
  $env:PYTHONPATH="src;."; python -m sentinelnutri.cli bootstrap --env dev
  ```
- Regenerar el CSV para Google Colab, reporte de métricas, matriz OEI/ODS y las 4 figuras de 300 DPI:
  ```powershell
  $env:PYTHONPATH="src;."; python -m sentinelnutri.cli export-artifacts
  ```
- Ejecutar las 22 pruebas unitarias, adversariales (Red-Team QA Fases 1–6) y de integración E2E:
  ```powershell
  $env:PYTHONPATH="src;."; python tests/run_all_tests.py
  ```

