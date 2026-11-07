-- ============================================================================
-- VISTAS ANALÍTICAS PARA LOS CANALES DEL MSV (S2, S3, S3*, S4 y S5)
-- ============================================================================

-- Vista 1: Homeostato S3-S4 (Estado Actual vs Proyección Futura por Distrito)
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
JOIN predicciones_dci p ON c.ubigeo = p.ubigeo;

-- Vista 2: Coordinación S2 por Red de Salud Provincial (7 Provincias)
CREATE OR REPLACE VIEW vw_coordinacion_s2_redes AS
SELECT
    c.provincia,
    c.red_salud,
    COUNT(DISTINCT c.ubigeo) AS total_distritos_monitoreados,
    ROUND(AVG(p.dci_actual_pct), 2) AS promedio_dci_actual,
    ROUND(AVG(p.dci_proyectada_pct), 2) AS promedio_dci_proyectada,
    SUM(CASE WHEN p.supera_umbral_algedonico THEN 1 ELSE 0 END) AS distritos_en_alerta_algedonica
FROM cat_ubigeo_hvc c
LEFT JOIN predicciones_dci p ON c.ubigeo = p.ubigeo
GROUP BY c.provincia, c.red_salud;

