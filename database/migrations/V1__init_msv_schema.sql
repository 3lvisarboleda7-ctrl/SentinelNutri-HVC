-- ============================================================================
-- MIGRACIÓN V1: Esquema Cibernético SentinelNutri-HVC (PostgreSQL 16)
-- Alineado al Modelo de Sistema Viable (S1, S2, S3, S3*, S4, S5) - GORE Huancavelica
-- ============================================================================

-- 1. Catálogo Oficial de Distritos y Redes de Salud de Huancavelica (S1 y S2)
CREATE TABLE IF NOT EXISTS cat_ubigeo_hvc (
    ubigeo VARCHAR(6) PRIMARY KEY,
    provincia VARCHAR(60) NOT NULL,
    distrito VARCHAR(80) NOT NULL,
    red_salud VARCHAR(80) NOT NULL,
    altitud_msnm INTEGER NOT NULL,
    latitud NUMERIC(9, 6) NOT NULL,
    longitud NUMERIC(9, 6) NOT NULL,
    poblacion_menor_5 INTEGER NOT NULL DEFAULT 500,
    ruralidad_pct NUMERIC(5, 2) NOT NULL DEFAULT 65.0
);

-- 2. Registro de Cargas y Trazabilidad de Extracción Automatizada (Tabla 4 del Proyecto)
CREATE TABLE IF NOT EXISTS registro_cargas (
    id SERIAL PRIMARY KEY,
    fuente VARCHAR(40) NOT NULL,               -- SIEN_HIS, ENDES, INEI_POBREZA, MEF_PAN, MIDIS, SENAMHI, DIRESA_LEY29733
    url_origen TEXT NOT NULL,
    fecha_publicacion_portal VARCHAR(40),
    fecha_consulta TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    hash_sha256 VARCHAR(64) NOT NULL,
    hubo_cambio BOOLEAN NOT NULL DEFAULT TRUE,
    ruta_archivo_crudo TEXT NOT NULL,          -- Ruta en el HDD de 1 TB del Equipo 2
    registros_procesados INTEGER NOT NULL DEFAULT 0,
    estado VARCHAR(30) NOT NULL DEFAULT 'OK',  -- OK, SIN_CAMBIOS, ERROR_DISENO_PORTAL
    detalle_mensaje TEXT
);

CREATE INDEX IF NOT EXISTS idx_registro_cargas_fuente_hash ON registro_cargas(fuente, hash_sha256);

-- 3. Serie Histórica Integrada por Ubigeo Distrital (2014-2024+) - Las 5 Dimensiones
CREATE TABLE IF NOT EXISTS serie_historica_distrital (
    id SERIAL PRIMARY KEY,
    ubigeo VARCHAR(6) NOT NULL REFERENCES cat_ubigeo_hvc(ubigeo),
    anio INTEGER NOT NULL,
    semestre INTEGER NOT NULL DEFAULT 2,       -- 1 o 2 (para cortes semestrales SIEN-HIS)
    -- Dimensión 1: Antropométrica y Nutricional (SIEN-HIS INS/CENAN)
    tasa_dci_pct NUMERIC(5, 2) NOT NULL,
    tasa_anemia_pct NUMERIC(5, 2) NOT NULL,
    tasa_bajo_peso_pct NUMERIC(5, 2) NOT NULL,
    niños_evaluados INTEGER NOT NULL DEFAULT 300,
    -- Dimensión 2: Socioeconómica (INEI Censos / Mapa de Pobreza / ENDES)
    pobreza_monetaria_pct NUMERIC(5, 2) NOT NULL,
    educacion_materna_secundaria_pct NUMERIC(5, 2) NOT NULL,
    -- Dimensión 3: Acceso a Servicios de Salud y Saneamiento (ENDES / INEI)
    agua_cloro_adecuado_pct NUMERIC(5, 2) NOT NULL,
    saneamiento_basico_pct NUMERIC(5, 2) NOT NULL,
    controles_cred_completo_pct NUMERIC(5, 2) NOT NULL,
    lactancia_materna_exclusiva_pct NUMERIC(5, 2) NOT NULL,
    -- Dimensión 4: Agroalimentaria, Presupuesto y Programas Sociales (MEF Consulta Amigable + MIDIS)
    ejecucion_pan_mef_pct NUMERIC(5, 2) NOT NULL,
    presupuesto_pan_per_capita_soles NUMERIC(10, 2) NOT NULL,
    cobertura_juntos_pct NUMERIC(5, 2) NOT NULL,
    cobertura_cuna_mas_pct NUMERIC(5, 2) NOT NULL,
    cobertura_qali_warma_pct NUMERIC(5, 2) NOT NULL,
    -- Dimensión 5: Climática (SENAMHI)
    dias_heladas_anual INTEGER NOT NULL,
    temp_minima_promedio_c NUMERIC(5, 2) NOT NULL,
    precipitacion_anual_mm NUMERIC(7, 2) NOT NULL,
    fecha_actualizacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ubigeo, anio, semestre)
);

CREATE INDEX IF NOT EXISTS idx_serie_ubigeo_anio ON serie_historica_distrital(ubigeo, anio DESC);

-- 4. Predicciones del Motor CatBoost + SHAP (Atenuador de Variedad S4 y Auditoría S3*)
CREATE TABLE IF NOT EXISTS predicciones_dci (
    id SERIAL PRIMARY KEY,
    ubigeo VARCHAR(6) NOT NULL REFERENCES cat_ubigeo_hvc(ubigeo),
    anio_base INTEGER NOT NULL,
    horizonte_proyeccion VARCHAR(20) NOT NULL DEFAULT 'PROXIMO_SEMESTRE',
    dci_actual_pct NUMERIC(5, 2) NOT NULL,
    dci_proyectada_pct NUMERIC(5, 2) NOT NULL,
    probabilidad_riesgo_critico NUMERIC(5, 4) NOT NULL,
    nivel_riesgo VARCHAR(20) NOT NULL,         -- BAJO, MODERADO, ALTO, CRITICO
    supera_umbral_algedonico BOOLEAN NOT NULL, -- REGLA FIJA: TRUE si dci_proyectada_pct > 25.0
    valores_shap_json TEXT NOT NULL,           -- JSON con contribuciones SHAP por variable (S3*)
    top_factores_riesgo TEXT NOT NULL,
    version_modelo VARCHAR(40) NOT NULL DEFAULT 'catboost_shap_v1',
    fecha_prediccion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 5. Informes Agénticos, Aprobación Humana (HITL) y Enrutamiento a Canales MSV (S3 y S5)
CREATE TABLE IF NOT EXISTS alertas_y_recomendaciones_msv (
    id SERIAL PRIMARY KEY,
    id_prediccion INTEGER REFERENCES predicciones_dci(id),
    ubigeo VARCHAR(6) NOT NULL REFERENCES cat_ubigeo_hvc(ubigeo),
    provincia VARCHAR(60) NOT NULL,
    nivel_riesgo VARCHAR(20) NOT NULL,
    canal_destino VARCHAR(30) NOT NULL,        -- S3_CONTROL o S5_ALGEDONICO
    sintesis_narrativa_s4 TEXT NOT NULL,
    recomendacion_salud TEXT NOT NULL,
    recomendacion_agua_saneamiento TEXT NOT NULL,
    recomendacion_agricultura_midis TEXT NOT NULL,
    oei_pei_vinculados VARCHAR(120) NOT NULL,  -- Ej. OEI.01, OEI.04, OEI.08 (PEI 2020-2027)
    ods_vinculados VARCHAR(60) NOT NULL,       -- ODS 2, ODS 3, ODS 6
    proveedor_llm VARCHAR(40) NOT NULL,        -- gemini-2.0-flash o ollama/llama3.2
    estado_aprobacion_humana VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE_APROBACION', -- PENDIENTE_APROBACION, APROBADO_S3, ALGEDONICO_DIRECTO_S5, RECHAZADO
    aprobado_por VARCHAR(80),
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_resolucion TIMESTAMP
);

