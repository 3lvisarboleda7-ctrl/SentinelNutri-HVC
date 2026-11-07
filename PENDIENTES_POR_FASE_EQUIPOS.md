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
- [x] **Implementación de las 3 Reglas Fijas y Guardarraíl Ley N.º 29733** (`[EQUIPO 1]` — **Completado y testeado 10/10**)
- [x] **Esqueleto funcional de las 6 Herramientas del Agente Supervisor en FastAPI** (`[EQUIPO 1]` — **Completado**)
- [ ] **Fase 1 (Semana 2):** Aprovisionamiento físico del servidor local y red entre ambos equipos.
- [ ] **Fase 2 (Semana 3):** Web scraping en vivo de los 6 portales estatales y catálogo de los 102 distritos.
- [ ] **Fase 3 (Semana 4):** Entrenamiento pesado en Google Colab y transferencia del modelo `.cbm` al Equipo 2.
- [ ] **Fase 4 (Semana 5):** Configuración del Agente Supervisor en `n8n`, Gemini API, Ollama GTX 1050 y bots de Telegram/Gmail.
- [ ] **Fase 5 (Semana 6):** Publicación de `Cloudflare Tunnel`, aprobación desde celular y pruebas con el Dashboard Streamlit.
- [ ] **Fase 6 (Semana 7):** Evaluación final XAI (SHAP), gobernanza, ODS 2, 3 y 6 y redacción del informe final.

---

## Detalle de Pendientes por Fase y por Equipo

### FASE 1 (Semana 2 del Cronograma): Entorno de Costo Cero e Infraestructura Dual

#### En el `[EQUIPO 1 · Estación de Desarrollo (Windows 11)]`
- [x] Diseñar la arquitectura Clean/Hexagonal (`domain`, `application`, `infrastructure`, `interfaces`).
- [x] Crear `deploy/docker-compose.equipo2.yml` separando volúmenes SSD (`C:\`) y HDD (`D:\`).
- [x] Crear los scripts PowerShell de aprovisionamiento para el Equipo 2 en `deploy/scripts_equipo2/`.
- [x] Implementar detector automático de máquina (`python -m sentinelnutri.cli whoami` en `src/sentinelnutri/config/node_detector.py`) por huella de hardware/SO (`i7-1355U` vs `i7-7700HQ` + `GTX 1050`).
- [x] Inicializar el repositorio Git local (`git init` + commits en rama `main`).
- [ ] Subir el repositorio local a **GitHub** (`git remote add origin ...` + `git push -u origin main`) para clonarlo fácilmente desde el Equipo 2.
- [ ] Anotar la dirección IP local (LAN) del Equipo 2 (ej. `192.168.1.XX`) y colocarla en `config/.env.equipo1` (`EQUIPO2_LAN_IP`).

#### En el `[EQUIPO 2 · Servidor Local (Windows 10 · SSD + HDD 1 TB · GTX 1050)]`
- [ ] Clonar el repositorio de GitHub en el **SSD** del Equipo 2 (ej. `C:\SentinelNutri\repo`).
- [ ] Ejecutar en PowerShell (como Administrador) el script `.\deploy\scripts_equipo2\01_setup_ssd_hdd_dirs.ps1` para crear automáticamente:
  - En el **SSD (`C:\SentinelNutri\ssd\`)**: `postgres_data` y `n8n_data`.
  - En el **HDD de 1 TB (`D:\SentinelNutri\hdd\`)**: `raw`, `models`, `backups`, `ollama_models` y `diresa_convenio_ley29733`.
- [ ] Ejecutar el script `.\deploy\scripts_equipo2\02_install_ollama_gpu.ps1` en el Equipo 2 para:
  - Verificar que `nvidia-smi` detecte la tarjeta **NVIDIA GTX 1050 (4 GB VRAM)**.
  - Instalar **Ollama** en Windows 10.
  - Fijar `OLLAMA_MODELS=D:\SentinelNutri\hdd\ollama_models` (para que los modelos se guarden en el disco duro de 1 TB y no ocupen el SSD).
  - Fijar `OLLAMA_HOST=0.0.0.0:11434` y descargar el modelo `llama3.2`.
- [ ] Copiar `config/.env.equipo2.example` a `config/.env.equipo2` y levantar la base de datos y los contenedores iniciales en el Equipo 2:
  ```powershell
  docker compose -f deploy/docker-compose.equipo2.yml --env-file config/.env.equipo2 up -d postgres api_engine
  ```

---

### FASE 2 (Semana 3 del Cronograma): Extracción Automatizada (Web Scraping) y Preprocesamiento

#### En el `[EQUIPO 1 · Estación de Desarrollo (Windows 11)]`
- [x] **Catálogo completo de Ubigeos:** Ampliar `src/sentinelnutri/infrastructure/persistence/database.py` a los **100 distritos oficiales de las 7 provincias de Huancavelica** (`090101` al `090721`, integrando `1 100` registros históricos 2014–2024).
- [ ] **Scraper 1 — SIEN-HIS (INS/CENAN) y Datos Abiertos (`sien_ins_scraper.py`):**
  - Programar la descarga automática de los archivos CSV/XLSX de la Plataforma Nacional de Datos Abiertos (`datosabiertos.gob.pe`) y reportes PDF del INS (2014–2024), extrayendo las tablas distritales de DCI, anemia y bajo peso con `pdfplumber` / `pymupdf`.
- [ ] **Scraper 2 — ENDES INEI (`endes_inei_scraper.py`):**
  - Programar la descarga automatizada de los módulos anuales de microdatos del portal INEI (`proyectos.inei.gob.pe/microdatos/`) y el filtrado del departamento `09 (Huancavelica)` con `pyreadstat` (agua con cloro adecuado, saneamiento, educación materna, lactancia y controles CRED).
- [ ] **Scraper 3 — INEI Censos y Mapa de Pobreza (`inei_pobreza_scraper.py`):**
  - Automatizar la descarga e ingesta de la tabla distrital de pobreza monetaria, NBI, ruralidad y población menor de 5 años.
- [ ] **Scraper 4 — MEF Consulta Amigable con Playwright (`mef_pan_playwright.py`):**
  - Programar los selectores DOM exactos en `Playwright` para navegar el portal de Consulta Amigable del MEF, seleccionar los años `2014` a `2024`, filtrar el Departamento `09: HUANCAVELICA` y la Categoría Presupuestal `0001: PROGRAMA ARTICULADO NUTRICIONAL`, y extraer PIM, Devengado y % de Ejecución por municipalidad distrital.
- [ ] **Scraper 5 — MIDIS con Playwright (`midis_playwright.py`):**
  - Programar los selectores `Playwright` en los tableros de REDinforma / InfoMIDIS para descargar la cobertura distrital de **Juntos**, **Cuna Más** y **Qali Warma**.
- [ ] **Scraper 6 — SENAMHI (`senamhi_scraper.py`):**
  - Programar la extracción de temperatura mínima, días de heladas y precipitación de las estaciones meteorológicas de Huancavelica y su asignación geográfica por altitud/cercanía a cada `ubigeo`.
- [ ] Ejecutar las pruebas unitarias de ética (`robots.txt`, rate-limiting y hash `SHA-256`) en el Equipo 1 antes de hacer `git push`.

#### En el `[EQUIPO 2 · Servidor Local (Windows 10 · SSD + HDD 1 TB)]`
- [ ] Hacer `git pull` de los scrapers terminados y reconstruir el contenedor `api_engine` en el SSD.
- [ ] Disparar la primera ejecución masiva en modo **`backfill` (2014–2024)**:
  ```powershell
  curl -X POST http://localhost:8000/tools/extraer_fuentes -H "Content-Type: application/json" -d "{\"mode\": \"backfill\", \"start_year\": 2014, \"end_year\": 2024, \"force_rebuild\": true}"
  ```
- [ ] Verificar que todos los archivos crudos descargados (`PDF`, `SAV`, `CSV`, `HTML`) hayan quedado guardados en el **HDD de 1 TB (`D:\SentinelNutri\hdd\raw\`)** y que la tabla `registro_cargas` en el **PostgreSQL del SSD** tenga las fechas y huellas digitales `SHA-256`.

---

### FASE 3 (Semana 4 del Cronograma): Motor Predictivo CatBoost + SHAP (XAI)

#### En el `[EQUIPO 1 -> GOOGLE COLAB (Entrenamiento Pesado en la Nube)]`
- [ ] Exportar el dataset histórico consolidado `2014–2024` desde la base de datos (`GET /tools/consultar_bd`) a un archivo `panel_distrital_hvc_2014_2024.csv`.
- [ ] Abrir Google Colab desde el navegador del **Equipo 1** y cargar el notebook `notebooks_colab/02_entrenamiento_catboost_shap_colab.ipynb`.
- [ ] Ejecutar en **Google Colab**:
  - Entrenamiento de `CatBoostClassifier` y `CatBoostRegressor` sobre las 5 dimensiones de variables.
  - Validación Cruzada Estratificada ($k=5$ folds) verificando que se supere la meta académica de **$\text{AUC-ROC} \ge 0,90$** (Navarro-Guillén et al., 2026), además de calcular $\text{F1-Score}$, precisión y *recall* por provincia y distrito.
  - Cálculo de `shap.TreeExplainer` y exportación de gráficos de alta resolución (*SHAP Beeswarm Global* y *SHAP Waterfall Local* de los distritos críticos) para el Capítulo 5 y 6 del informe.
  - Descargar al **Equipo 1** los artefactos entrenados: `catboost_dci_hvc.cbm`, `shap_explainer.pkl` y `metrics_report.json`.

#### En el `[EQUIPO 2 · Servidor Local (Windows 10 · HDD 1 TB + SSD)]`
- [ ] Copiar por red local (LAN) el modelo entrenado `catboost_dci_hvc.cbm` y `shap_explainer.pkl` desde el Equipo 1 hacia la carpeta del **HDD de 1 TB del Equipo 2**: `D:\SentinelNutri\hdd\models\`.
- [ ] Verificar desde el Equipo 1 que el endpoint `POST http://<IP_EQUIPO_2>:8000/predict` y `GET http://<IP_EQUIPO_2>:8000/tools/explicar_riesgo/090411` carguen el modelo del HDD y devuelvan las predicciones y valores SHAP en menos de 1 segundo.

---

### FASE 4 (Semana 5 del Cronograma): Módulo Agéntico en n8n, 6 Herramientas y Reglas Fijas

#### En el `[EQUIPO 1 · Estación de Desarrollo (Windows 11)]`
- [ ] Obtener las credenciales gratuitas de los servicios externos:
  1. **Google AI Studio:** Crear API Key gratuita de **Gemini** (`GEMINI_API_KEY`).
  2. **Telegram (`@BotFather`):** Crear el bot `@SentinelNutriHVC_Bot`, obtener `TELEGRAM_BOT_TOKEN` y los `CHAT_ID` para el **Consejo Regional (S5)**, la **Gerencia Regional de Desarrollo Social (S3)** y **Alertas Técnicas de Fallos de Scraper**.
  3. **Gmail:** Crear una *Contraseña de Aplicación* (`GMAIL_APP_PASSWORD`) en la cuenta de Google del proyecto.
- [ ] Ajustar en `workflows_n8n/01_ciclo_supervisor_sentinelnutri.json` y `02_vigilancia_fallos_scrapers.json` los nombres de credenciales si fuera necesario.

#### En el `[EQUIPO 2 · Servidor Local (Windows 10 · SSD + GPU GTX 1050)]`
- [ ] Colocar las claves `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN` y `GMAIL_APP_PASSWORD` en `config/.env.equipo2`.
- [ ] Levantar el contenedor de `n8n` en el SSD del Equipo 2:
  ```powershell
  docker compose -f deploy/docker-compose.equipo2.yml --env-file config/.env.equipo2 up -d n8n
  ```
- [ ] Acceder a la interfaz web de `n8n` desde el navegador del **Equipo 1** (`http://<IP_EQUIPO_2>:5678`) e importar los 2 flujos de `workflows_n8n/`:
  1. `01_ciclo_supervisor_sentinelnutri.json` (Agente Supervisor con sus **6 herramientas** + **Regla Fija 1** `Schedule Trigger` + **Regla Fija 2** `Nodo IF DCI > 25% -> S5` + **Regla Fija 3** `Aprobación Humana Telegram/Gmail -> S3`).
  2. `02_vigilancia_fallos_scrapers.json` (Autodiagnóstico por Telegram cuando un portal cambia de diseño).
- [ ] Probar la conmutación automática del nodo `AI Agent`: verificar que responda primero con **Gemini Free Tier** y, al desconectar internet o simular fin de cuota, responda con **Ollama (`llama3.2`) acelerado por la GPU GTX 1050** del Equipo 2.

---

### FASE 5 (Semana 6 del Cronograma): Cloudflare Tunnel, Aprobación desde Celular y Dashboard Streamlit

#### En el `[EQUIPO 2 · Servidor Local (Windows 10 · SSD)]`
- [ ] Crear el túnel gratuito en **Cloudflare Zero Trust** (`Networks -> Tunnels`), copiar el token en `config/.env.equipo2` (`CLOUDFLARE_TUNNEL_TOKEN`) y apuntar el subdominio HTTPS hacia `http://n8n:5678`.
- [ ] Levantar los contenedores `dashboard` (Streamlit) y `cloudflared` (Cloudflare Tunnel) en el Equipo 2:
  ```powershell
  docker compose -f deploy/docker-compose.equipo2.yml --env-file config/.env.equipo2 up -d dashboard cloudflared
  ```
- [ ] Programar en el Programador de Tareas de Windows 10 del Equipo 2 el script `.\deploy\scripts_equipo2\04_backup_postgres_to_hdd.ps1` para que cada semana guarde una copia de seguridad de PostgreSQL (SSD) en el **HDD de 1 TB (`D:\SentinelNutri\hdd\backups\`)**.

#### En `[AMBOS EQUIPOS + Celular (Pruebas de Canales MSV)]`
- [ ] **Prueba del Canal Algedónico Automatizado (S1/S4 $\rightarrow$ S5):** Ejecutar el flujo con un distrito cuya DCI proyectada supere el **25 %** (ej. `Santa Ana 090411` o `Paucará 090206`) y verificar que la alerta llegue **de inmediato** al celular por Telegram y Gmail sin esperar aprobación humana.
- [ ] **Prueba del Canal de Control con Aprobación Humana (S4 $\rightarrow$ S3 vía Cloudflare Tunnel):** Recibir en el celular la propuesta de recomendación sectorial (Salud, Agua, Agricultura - OEI PEI 2020–2027), pulsar **Aprobar** a través del enlace HTTPS seguro de **Cloudflare Tunnel** (sin abrir puertos del router en Windows 10) y comprobar desde el **Equipo 1** (`http://<IP_EQUIPO_2>:8501`) que la recomendación aparece publicada como `APROBADO_S3` en el Dashboard Streamlit.

---

### FASE 6 (Semana 7 del Cronograma): Evaluación XAI, Gobernanza y Documentación Final

#### En el `[EQUIPO 1 · Estación de Desarrollo (Windows 11)]`
- [ ] Ejecutar el notebook `notebooks_colab/03_evaluacion_xai_y_gobernanza.ipynb` para generar las tablas y figuras definitivas del **Capítulo 6 y 7 del Informe Final**:
  - Tabla de métricas de desempeño ($\text{AUC}$, $\text{F1}$, precisión por provincia y distrito).
  - Análisis de explicabilidad XAI (valores SHAP globales y casos de estudio distritales para la auditoría **S3***).
  - Evidencia de cumplimiento del marco ético: verificación de la **Ley N.º 29733** (solo agregados distritales hacia Gemini), respeto a `robots.txt` y bitácora de hashes `SHA-256`.
  - Matriz de articulación con los **OEI del PEI 2020–2027** del GORE Huancavelica y los **ODS 2, 3 y 6**.
  - Capturas de pantalla del Dashboard Streamlit, del flujo del Agente Supervisor en `n8n` y de las alertas en Telegram/Gmail corriendo sobre la infraestructura dual Equipo 1 / Equipo 2.

