-- ============================================================================
-- MIGRACIÓN V3: Persistencia Criptográfica SHA-256 de Alertas y Resoluciones HITL
-- No repudio en el Canal de Auditoría S3* y Canal de Control S3 (GORE Huancavelica)
-- ============================================================================

ALTER TABLE alertas_y_recomendaciones_msv
    ADD COLUMN IF NOT EXISTS huella_auditoria_sha256 VARCHAR(64),
    ADD COLUMN IF NOT EXISTS huella_resolucion_sha256 VARCHAR(64);

CREATE INDEX IF NOT EXISTS idx_alertas_huella_sha256
    ON alertas_y_recomendaciones_msv(huella_auditoria_sha256);
