# SentinelNutri-HVC: Sistema Inteligente de Alerta Temprana para el Sistema 4 del MSV (Región Huancavelica)

**Curso:** Modelo de Sistema Viable (MSV) — Prof. Ricardo Rodríguez-Ulloa  
**Autor:** Elvis Arboleda — Facultad de Ingeniería Industrial y de Sistemas (FIIS), Universidad Nacional de Ingeniería (UNI)  
**Marcos de Referencia:** Modelo de Sistema Viable (Beer, 1979, 1985; Pérez Ríos, 2025), Ley de la Variedad Requerida (Ashby, 1956), Marco AIM-IS (Fontaine et al., 2026), Guía de IA en el Sector Público CEPAL (Clavijo, 2026), CatBoost-SHAP XAI (Navarro-Guillén et al., 2026; Castro-Bedriñana et al., 2021) y Arquitecturas Agénticas para Políticas Públicas (Wang et al., 2026).

---

## 1. Propósito Cibernético y Arquitectura del Sistema

**SentinelNutri-HVC** se integra al **Sistema 4 (Inteligencia)** del Gobierno Regional de Huancavelica (**GORE-HVC**, Nivel 1 del MSV) para resolver la patología de *parálisis por análisis* y el desbalance de variedad frente a la **Desnutrición Crónica Infantil (DCI: 20,3 % en 2025 vs. 12,1 % nacional)**.

Combina cuatro estilos arquitectónicos modernos con **costo de licencias igual a cero**:
1. **Microservicios Contenedorizados (`Docker Compose`):** `n8n`, `FastAPI + Playwright`, `PostgreSQL`, `Streamlit`, `Cloudflare Tunnel` y `Ollama` (respaldo local acelerado por GPU).
2. **Arquitectura Orientada a Eventos (`EDA`) + Aprobación Humana (`HITL`):** Reacciona a eventos semanales (`Schedule Trigger`), cambios en portales públicos (`SHA-256`), excesos de umbral crítico (`DCI proyectada > 25 %`) y aprobaciones humanas desde el celular vía HTTPS seguro (**Cloudflare Tunnel**).
3. **Arquitectura Agéntica de Supervisor con 6 Herramientas y 3 Reglas Fijas:** Un **Agente Supervisor** en `n8n` (conectado a **Gemini Free Tier** y respaldado por **Llama 3.2 en Ollama**) decide el orden de ejecución de **6 herramientas** (`extraer_fuentes`, `consultar_bd`, `predecir_riesgo`, `explicar_riesgo`, `redactar_informe`, `notificar`), mientras que **3 decisiones críticas quedan en reglas fijas deterministas**:
   - **Regla Fija 1 (Predicción):** El riesgo numérico lo calcula **CatBoost** (`/predict`), nunca el LLM.
   - **Regla Fija 2 (Canal Algedónico S1/S4 $\rightarrow$ S5):** Si `DCI proyectada > 25 %`, un nodo `IF` envía **siempre** una señal algedónica al **Consejo Regional (S5)** por Telegram y Gmail.
   - **Regla Fija 3 (Aprobación Humana $\rightarrow$ S3):** Ninguna recomendación llega al **Canal de Control (S3 - Gerencia Regional de Desarrollo Social)** sin antes recibir aprobación de un responsable humano por Telegram o Gmail.
4. **Clean / Hexagonal Architecture + Cookiecutter Data Science:** Separación estricta entre `domain`, `application`, `infrastructure` e `interfaces`.

---

## 2. Infraestructura Dual de Costo Cero (Equipo 1 + Google Colab + Equipo 2)

| Rol | Equipo | Especificaciones | Qué aloja / ejecuta |
| :--- | :--- | :--- | :--- |
| **Estación de Desarrollo** | **Equipo 1** | Intel Core i7-1355U; 16 GB RAM; SSD 477 GB; Windows 11 Pro | Desarrollo en VS Code, pruebas automatizadas (`pytest`), ejecución de notebooks en **Google Colab** (entrenamiento pesado `CatBoost + SHAP`) y acceso por red local (LAN) a `n8n` y al `Dashboard Streamlit`. |
| **Servidor Local** | **Equipo 2** | Intel Core i7-7700HQ; 16 GB RAM; **GPU NVIDIA GTX 1050 (4 GB)**; **SSD 447 GB** + **HDD 1 TB**; Windows 10 | **En SSD (`C:\SentinelNutri`):** Docker, `n8n`, `PostgreSQL`, `FastAPI + Playwright`, `Streamlit`, `Cloudflare Tunnel` y `Ollama` (acelerado por GPU GTX 1050).<br/>**En HDD (`D:\SentinelNutri`):** Archivos crudos descargados (`/raw`), respaldos de BD (`/backups`), modelos entrenados (`/models`) y pesos de Ollama. |

---

## 3. Estructura del Proyecto

```text
SentinelNutri-HVC/
├── config/                  # Plantillas .env para Equipo 1 y Equipo 2 + configuración de logs
├── deploy/                  # Docker Compose (Equipo 2 y Dev) + Scripts PowerShell (SSD/HDD, Ollama GTX 1050, Cloudflare Tunnel)
├── database/                # Migraciones SQL (Esquema MSV, Catálogo de las 7 provincias de Huancavelica y Vistas S2/S3/S3*/S5)
├── src/sentinelnutri/       # Código fuente bajo Clean / Hexagonal Architecture
│   ├── domain/              # Entidades MSV, Reglas Fijas (umbral 25%, Ley 29733 privacidad, ética robots.txt) y Puertos
│   ├── application/         # Las 6 Herramientas del Agente Supervisor (Casos de Uso)
│   ├── infrastructure/      # Adaptadores: PostgreSQL/SQLite, Scrapers (SIEN, ENDES, INEI, MEF, MIDIS, SENAMHI), CatBoost, SHAP
│   └── interfaces/          # Microservicio REST FastAPI (:8000) y Dashboard Cibernético Streamlit (:8501)
├── workflows_n8n/           # Flujos JSON importables en n8n (Agente Supervisor + Reglas Fijas + Alerta de Fallo de Scraper)
├── notebooks_colab/         # Notebooks para Google Colab (Backfill 2014-2024, Entrenamiento CatBoost+SHAP y Evaluación XAI)
└── tests/                   # Suite de pruebas unitarias e integrales (pytest)
```

---

## 4. Guía Rápida de Uso

### A. En el Equipo 1 (Estación de Desarrollo - Windows 11)
```powershell
# 1. Instalar dependencias de desarrollo y pruebas
pip install -r requirements-dev.txt

# 2. Inicializar base de datos local de desarrollo, ejecutar backfill y entrenar modelo base local
python -m sentinelnutri.cli bootstrap --env dev

# 3. Ejecutar la suite completa de pruebas (Reglas Fijas, Privacidad Ley 29733, Ética y las 6 Herramientas)
pytest -v

# 4. Levantar API FastAPI (:8000) o Dashboard Streamlit (:8501) en modo desarrollo
uvicorn sentinelnutri.interfaces.api.main:app --reload --port 8000 --app-dir src
streamlit run src/sentinelnutri/interfaces/dashboard/app.py
```

### B. En el Equipo 2 (Servidor Local - Windows 10 con SSD + HDD 1 TB + GTX 1050)
```powershell
# 1. Crear directorios en SSD (C:\SentinelNutri) y HDD de 1 TB (D:\SentinelNutri)
.\deploy\scripts_equipo2\01_setup_ssd_hdd_dirs.ps1

# 2. Instalar Ollama con soporte GPU NVIDIA GTX 1050 (4 GB) y almacenar modelos en HDD D:\
.\deploy\scripts_equipo2\02_install_ollama_gpu.ps1

# 3. Levantar los contenedores del sistema en el Equipo 2
docker compose -f deploy/docker-compose.equipo2.yml --env-file config/.env.equipo2 up -d --build
```

