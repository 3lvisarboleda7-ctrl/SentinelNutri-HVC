-- ============================================================================
-- VISTAS ANALÍTICAS PARA LOS CANALES DEL MSV (S2, S3, S3*, S4 y S5)
-- Filtradas sobre el corte más reciente por distrito y con trazabilidad SHA-256 (V3)
-- ============================================================================

-- Vista 1: Homeostato S3-S4 (Última Predicción por Distrito vs. Línea Base S3)
CREATE OR REPLACE VIEW vw_homeostato_s3_s4 AS
SELECT
    c.ubigeo,
    c.provincia,
    c.distrito,
    c.red_salud,
    c.altitud_msnm,
    p.dci_actual_pct,
    p.dci_proyectada_pct,
    (p.dci_proyectada_pct - p.dci_actual_pct) AS brecha_proyectada_pct,
    p.probabilidad_riesgo_critico,
    p.nivel_riesgo,
    p.supera_umbral_algedonico,
    p.top_factores_riesgo,
    p.fecha_prediccion
FROM cat_ubigeo_hvc c
JOIN (
    SELECT ubigeo, MAX(id) AS max_id
    FROM predicciones_dci
    GROUP BY ubigeo
) latest ON c.ubigeo = latest.ubigeo
JOIN predicciones_dci p ON p.id = latest.max_id;

-- Vista 2: Coordinación S2 por Red de Salud Provincial (7 Provincias sobre corte más reciente)
CREATE OR REPLACE VIEW vw_coordinacion_s2_redes AS
SELECT
    c.provincia,
    c.red_salud,
    COUNT(DISTINCT c.ubigeo) AS total_distritos_monitoreados,
    ROUND(AVG(p.dci_actual_pct), 2) AS promedio_dci_actual,
    ROUND(AVG(p.dci_proyectada_pct), 2) AS promedio_dci_proyectada,
    SUM(CASE WHEN p.supera_umbral_algedonico THEN 1 ELSE 0 END) AS distritos_en_alerta_algedonica
FROM cat_ubigeo_hvc c
LEFT JOIN (
    SELECT ubigeo, MAX(id) AS max_id
    FROM predicciones_dci
    GROUP BY ubigeo
) latest ON c.ubigeo = latest.ubigeo
LEFT JOIN predicciones_dci p ON p.id = latest.max_id
GROUP BY c.provincia, c.red_salud;

-- Vista 3: Canal Algedónico Directo S5 (Distritos con DCI Proyectada > 25.0%)
CREATE OR REPLACE VIEW vw_canal_algedonico_s5 AS
SELECT
    ubigeo,
    provincia,
    distrito,
    red_salud,
    altitud_msnm,
    dci_actual_pct,
    dci_proyectada_pct,
    brecha_proyectada_pct,
    nivel_riesgo,
    top_factores_riesgo,
    fecha_prediccion
FROM vw_homeostato_s3_s4
WHERE supera_umbral_algedonico = TRUE
ORDER BY dci_proyectada_pct DESC;

-- Vista 4: Auditoría S3* y Compuerta HITL S3 con Huellas Criptográficas SHA-256 (Migración V3)
CREATE OR REPLACE VIEW vw_auditoria_alertas_hitl_sha256 AS
SELECT
    a.id AS id_alerta,
    a.ubigeo,
    a.provincia,
    c.distrito,
    c.red_salud,
    a.nivel_riesgo,
    a.canal_destino,
    a.estado_aprobacion_humana,
    a.aprobado_por,
    a.proveedor_llm,
    a.oei_pei_vinculados,
    a.ods_vinculados,
    a.huella_auditoria_sha256,
    a.huella_resolucion_sha256,
    a.fecha_creacion,
    a.fecha_resolucion
FROM alertas_y_recomendaciones_msv a
JOIN cat_ubigeo_hvc c ON a.ubigeo = c.ubigeo
ORDER BY a.id DESC;
