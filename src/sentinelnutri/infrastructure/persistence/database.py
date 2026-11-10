"""
Configuración de Base de Datos Dual y Catálogo Oficial Completo de los 100 Distritos de Huancavelica:
- En Equipo 2 (Servidor Local): Conecta a PostgreSQL 16 (`postgresql+psycopg2://...`).
- En Equipo 1 (Estación de Desarrollo): Usa `sqlite3` nativo de Python, permitiendo ejecutar toda la
  arquitectura localmente con los 100 distritos de las 7 provincias (Huancavelica, Acobamba, Angaraes,
  Castrovirreyna, Churcampa, Huaytará y Tayacaja).
"""

import os
import sqlite3
from typing import Any, List, Tuple
from sentinelnutri.domain.entities.district import DistrictMetadata

# Los 100 distritos oficiales de las 7 provincias del departamento de Huancavelica (Ubigeo 09xxxx)
DEFAULT_HUANCAVELICA_DISTRICTS: List[DistrictMetadata] = [
    # 1. Provincia de Huancavelica (19 distritos)
    DistrictMetadata("090101", "Huancavelica", "Huancavelica", "Red de Salud Huancavelica", 3676, -12.7861, -74.9764, 4120, 22.5),
    DistrictMetadata("090102", "Huancavelica", "Acobambilla", "Red de Salud Huancavelica", 3795, -12.6542, -75.2819, 390, 84.0),
    DistrictMetadata("090103", "Huancavelica", "Acoria", "Red de Salud Huancavelica", 3167, -12.6378, -74.8614, 2450, 78.4),
    DistrictMetadata("090104", "Huancavelica", "Conayca", "Red de Salud Huancavelica", 3682, -12.5667, -75.0083, 180, 68.0),
    DistrictMetadata("090105", "Huancavelica", "Cuenca", "Red de Salud Huancavelica", 3167, -12.5931, -75.0681, 260, 82.0),
    DistrictMetadata("090106", "Huancavelica", "Huachocolpa", "Red de Salud Huancavelica", 3956, -13.0569, -74.9917, 340, 85.0),
    DistrictMetadata("090107", "Huancavelica", "Huayllahuara", "Red de Salud Huancavelica", 3896, -12.6208, -75.1583, 150, 79.0),
    DistrictMetadata("090108", "Huancavelica", "Huando", "Red de Salud Huancavelica", 3562, -12.5625, -74.9453, 810, 76.2),
    DistrictMetadata("090109", "Huancavelica", "Izcuchaca", "Red de Salud Huancavelica", 2939, -12.4969, -74.9961, 140, 42.0),
    DistrictMetadata("090110", "Huancavelica", "Laria", "Red de Salud Huancavelica", 3861, -12.6056, -75.0250, 190, 81.0),
    DistrictMetadata("090111", "Huancavelica", "Manta", "Red de Salud Huancavelica", 3727, -12.6278, -75.1889, 210, 83.5),
    DistrictMetadata("090112", "Huancavelica", "Mariscal Cáceres", "Red de Salud Huancavelica", 2847, -12.5361, -74.9528, 120, 58.0),
    DistrictMetadata("090113", "Huancavelica", "Moya", "Red de Salud Huancavelica", 3162, -12.5333, -75.1389, 220, 77.0),
    DistrictMetadata("090114", "Huancavelica", "Nuevo Occoro", "Red de Salud Huancavelica", 3825, -12.5861, -75.0750, 290, 84.2),
    DistrictMetadata("090115", "Huancavelica", "Palca", "Red de Salud Huancavelica", 3650, -12.6611, -74.9778, 360, 80.5),
    DistrictMetadata("090116", "Huancavelica", "Pilchaca", "Red de Salud Huancavelica", 3584, -12.5222, -75.0750, 130, 75.0),
    DistrictMetadata("090117", "Huancavelica", "Vilca", "Red de Salud Huancavelica", 3275, -12.5889, -75.1778, 310, 82.0),
    DistrictMetadata("090118", "Huancavelica", "Yauli", "Red de Salud Huancavelica", 3391, -12.7697, -74.8511, 3150, 81.5),
    DistrictMetadata("090119", "Huancavelica", "Ascensión", "Red de Salud Huancavelica", 3650, -12.7800, -74.9800, 1480, 31.0),
    # 2. Provincia de Acobamba (8 distritos)
    DistrictMetadata("090201", "Acobamba", "Acobamba", "Red de Salud Acobamba", 3423, -12.8419, -74.5694, 1180, 48.0),
    DistrictMetadata("090202", "Acobamba", "Andabamba", "Red de Salud Acobamba", 3460, -12.7483, -74.6214, 520, 88.5),
    DistrictMetadata("090203", "Acobamba", "Anta", "Red de Salud Acobamba", 3600, -12.8111, -74.6528, 790, 89.0),
    DistrictMetadata("090204", "Acobamba", "Caja", "Red de Salud Acobamba", 3512, -12.9278, -74.5028, 280, 83.0),
    DistrictMetadata("090205", "Acobamba", "Marcas", "Red de Salud Acobamba", 3394, -12.9667, -74.5250, 260, 81.0),
    DistrictMetadata("090206", "Acobamba", "Paucará", "Red de Salud Acobamba", 3806, -12.7239, -74.6711, 2290, 82.1),
    DistrictMetadata("090207", "Acobamba", "Pomacocha", "Red de Salud Acobamba", 3150, -12.8889, -74.5361, 410, 79.5),
    DistrictMetadata("090208", "Acobamba", "Rosario", "Red de Salud Acobamba", 3640, -12.7686, -74.6142, 740, 86.4),
    # 3. Provincia de Angaraes (12 distritos)
    DistrictMetadata("090301", "Angaraes", "Lircay", "Red de Salud Angaraes", 3278, -12.9894, -74.7208, 2890, 56.3),
    DistrictMetadata("090302", "Angaraes", "Anchonga", "Red de Salud Angaraes", 3298, -12.9369, -74.7450, 860, 87.2),
    DistrictMetadata("090303", "Angaraes", "Callanmarca", "Red de Salud Angaraes", 3526, -12.9167, -74.6667, 150, 84.0),
    DistrictMetadata("090304", "Angaraes", "Ccochaccasa", "Red de Salud Angaraes", 4150, -12.9278, -74.7981, 380, 79.0),
    DistrictMetadata("090305", "Angaraes", "Chincho", "Red de Salud Angaraes", 3134, -13.0111, -74.4778, 190, 88.0),
    DistrictMetadata("090306", "Angaraes", "Congalla", "Red de Salud Angaraes", 3528, -13.0278, -74.5972, 490, 86.5),
    DistrictMetadata("090307", "Angaraes", "Huanca-Huanca", "Red de Salud Angaraes", 3567, -12.9667, -74.6528, 210, 83.0),
    DistrictMetadata("090308", "Angaraes", "Huayllay Grande", "Red de Salud Angaraes", 3625, -12.9389, -74.6917, 180, 75.0),
    DistrictMetadata("090309", "Angaraes", "Julcamarca", "Red de Salud Angaraes", 3418, -13.0250, -74.4417, 230, 78.0),
    DistrictMetadata("090310", "Angaraes", "San Antonio de Antaparco", "Red de Salud Angaraes", 2771, -13.1167, -74.5167, 290, 87.0),
    DistrictMetadata("090311", "Angaraes", "Santo Tomás de Pata", "Red de Salud Angaraes", 3156, -13.1056, -74.4583, 210, 86.0),
    DistrictMetadata("090312", "Angaraes", "Secclla", "Red de Salud Angaraes", 3340, -13.0956, -74.5819, 410, 85.1),
    # 4. Provincia de Castrovirreyna (13 distritos)
    DistrictMetadata("090401", "Castrovirreyna", "Castrovirreyna", "Red de Salud Castrovirreyna", 3956, -13.2806, -75.3183, 390, 62.0),
    DistrictMetadata("090402", "Castrovirreyna", "Arma", "Red de Salud Castrovirreyna", 3336, -13.1667, -75.4667, 180, 79.0),
    DistrictMetadata("090403", "Castrovirreyna", "Aurahuá", "Red de Salud Castrovirreyna", 3470, -13.0833, -75.5333, 240, 81.0),
    DistrictMetadata("090404", "Castrovirreyna", "Capillas", "Red de Salud Castrovirreyna", 3218, -13.3667, -75.5333, 170, 82.5),
    DistrictMetadata("090405", "Castrovirreyna", "Chupamarca", "Red de Salud Castrovirreyna", 3325, -13.0333, -75.5833, 160, 84.0),
    DistrictMetadata("090406", "Castrovirreyna", "Cocas", "Red de Salud Castrovirreyna", 3246, -13.2667, -75.3833, 150, 80.0),
    DistrictMetadata("090407", "Castrovirreyna", "Huachos", "Red de Salud Castrovirreyna", 2737, -13.2325, -75.5347, 190, 77.5),
    DistrictMetadata("090408", "Castrovirreyna", "Huamatambo", "Red de Salud Castrovirreyna", 3056, -13.1833, -75.5500, 110, 83.0),
    DistrictMetadata("090409", "Castrovirreyna", "Mollepampa", "Red de Salud Castrovirreyna", 2465, -13.3167, -75.4667, 180, 78.0),
    DistrictMetadata("090410", "Castrovirreyna", "San Juan", "Red de Salud Castrovirreyna", 1916, -13.2500, -75.6000, 120, 76.0),
    DistrictMetadata("090411", "Castrovirreyna", "Santa Ana", "Red de Salud Castrovirreyna", 4473, -13.0681, -75.1419, 210, 91.0),
    DistrictMetadata("090412", "Castrovirreyna", "Tantara", "Red de Salud Castrovirreyna", 2882, -13.1333, -75.5667, 130, 79.0),
    DistrictMetadata("090413", "Castrovirreyna", "Ticrapo", "Red de Salud Castrovirreyna", 2184, -13.3833, -75.4333, 210, 72.0),
    # 5. Provincia de Churcampa (11 distritos)
    DistrictMetadata("090501", "Churcampa", "Churcampa", "Red de Salud Churcampa", 3262, -12.7258, -74.3881, 640, 58.0),
    DistrictMetadata("090502", "Churcampa", "Anco", "Red de Salud Churcampa", 2404, -12.6331, -74.5875, 1020, 86.0),
    DistrictMetadata("090503", "Churcampa", "Chinchihuasi", "Red de Salud Churcampa", 2800, -12.5000, -74.5500, 480, 87.5),
    DistrictMetadata("090504", "Churcampa", "El Carmen", "Red de Salud Churcampa", 3114, -12.6833, -74.4500, 360, 84.0),
    DistrictMetadata("090505", "Churcampa", "La Merced", "Red de Salud Churcampa", 2632, -12.7667, -74.3500, 190, 75.0),
    DistrictMetadata("090506", "Churcampa", "Locroja", "Red de Salud Churcampa", 3379, -12.6667, -74.4167, 450, 85.0),
    DistrictMetadata("090507", "Churcampa", "Paucarbamba", "Red de Salud Churcampa", 3370, -12.5594, -74.5361, 690, 84.5),
    DistrictMetadata("090508", "Churcampa", "San Miguel de Mayocc", "Red de Salud Churcampa", 2212, -12.8000, -74.3833, 150, 71.0),
    DistrictMetadata("090509", "Churcampa", "San Pedro de Coris", "Red de Salud Churcampa", 3580, -12.5681, -74.4056, 430, 82.0),
    DistrictMetadata("090510", "Churcampa", "Pachamarca", "Red de Salud Churcampa", 2730, -12.4833, -74.4833, 320, 88.0),
    DistrictMetadata("090511", "Churcampa", "Cosme", "Red de Salud Churcampa", 3465, -12.6167, -74.6167, 410, 86.0),
    # 6. Provincia de Huaytará (16 distritos)
    DistrictMetadata("090601", "Huaytará", "Huaytará", "Red de Salud Huaytará", 2658, -13.6042, -75.3531, 260, 54.0),
    DistrictMetadata("090602", "Huaytará", "Ayaví", "Red de Salud Huaytará", 3758, -13.5667, -75.2500, 130, 84.0),
    DistrictMetadata("090603", "Huaytará", "Córdova", "Red de Salud Huaytará", 3216, -13.9833, -75.1833, 210, 83.0),
    DistrictMetadata("090604", "Huaytará", "Huayacundo Arma", "Red de Salud Huaytará", 3150, -13.5333, -75.3667, 110, 81.0),
    DistrictMetadata("090605", "Huaytará", "Laramarca", "Red de Salud Huaytará", 3342, -13.9167, -75.1167, 180, 85.0),
    DistrictMetadata("090606", "Huaytará", "Ocoyo", "Red de Salud Huaytará", 1953, -13.8833, -75.2000, 190, 82.0),
    DistrictMetadata("090607", "Huaytará", "Pilpichaca", "Red de Salud Huaytará", 4092, -13.3328, -75.0169, 440, 92.3),
    DistrictMetadata("090608", "Huaytará", "Querco", "Red de Salud Huaytará", 2856, -13.8000, -75.0333, 150, 86.0),
    DistrictMetadata("090609", "Huaytará", "Quito-Arma", "Red de Salud Huaytará", 2956, -13.5167, -75.4000, 140, 84.0),
    DistrictMetadata("090610", "Huaytará", "San Antonio de Cusicancha", "Red de Salud Huaytará", 3223, -13.4833, -75.3000, 210, 87.0),
    DistrictMetadata("090611", "Huaytará", "San Francisco de Sangayaico", "Red de Salud Huaytará", 3380, -13.6833, -75.2333, 140, 85.0),
    DistrictMetadata("090612", "Huaytará", "San Isidro", "Red de Salud Huaytará", 3615, -13.7333, -75.2667, 150, 84.0),
    DistrictMetadata("090613", "Huaytará", "Santiago de Chocorvos", "Red de Salud Huaytará", 2570, -13.8286, -75.2758, 310, 88.0),
    DistrictMetadata("090614", "Huaytará", "Santiago de Quirahuara", "Red de Salud Huaytará", 2802, -13.7833, -75.1500, 120, 86.0),
    DistrictMetadata("090615", "Huaytará", "Santo Domingo de Capillas", "Red de Salud Huaytará", 3367, -13.6167, -75.2000, 140, 85.0),
    DistrictMetadata("090616", "Huaytará", "Tambo", "Red de Salud Huaytará", 3141, -13.5833, -75.2333, 120, 83.0),
    # 7. Provincia de Tayacaja (21 distritos)
    DistrictMetadata("090701", "Tayacaja", "Pampas", "Red de Salud Tayacaja", 3276, -12.3986, -74.8689, 1340, 44.5),
    DistrictMetadata("090702", "Tayacaja", "Acostambo", "Red de Salud Tayacaja", 3597, -12.3611, -75.0542, 470, 81.0),
    DistrictMetadata("090703", "Tayacaja", "Acraquia", "Red de Salud Tayacaja", 3287, -12.3833, -74.9500, 520, 76.0),
    DistrictMetadata("090704", "Tayacaja", "Ahuaycha", "Red de Salud Tayacaja", 3280, -12.3833, -74.9167, 560, 79.0),
    DistrictMetadata("090705", "Tayacaja", "Colcabamba", "Red de Salud Tayacaja", 2979, -12.4119, -74.6775, 2150, 83.4),
    DistrictMetadata("090706", "Tayacaja", "Daniel Hernández", "Red de Salud Tayacaja", 3280, -12.3833, -74.8500, 980, 62.0),
    DistrictMetadata("090707", "Tayacaja", "Huachocolpa", "Red de Salud Tayacaja", 2907, -12.1592, -74.5944, 580, 89.2),
    DistrictMetadata("090708", "Tayacaja", "Huaribamba", "Red de Salud Tayacaja", 2996, -12.3167, -74.9667, 810, 85.0),
    DistrictMetadata("090709", "Tayacaja", "Ñahuimpuquio", "Red de Salud Tayacaja", 3630, -12.3333, -75.0667, 240, 78.0),
    DistrictMetadata("090710", "Tayacaja", "Pazos", "Red de Salud Tayacaja", 3840, -12.2500, -75.0667, 760, 83.0),
    DistrictMetadata("090711", "Tayacaja", "Quishuar", "Red de Salud Tayacaja", 3130, -12.3500, -74.7667, 140, 86.0),
    DistrictMetadata("090712", "Tayacaja", "Salcabamba", "Red de Salud Tayacaja", 3037, -12.2167, -74.7833, 540, 87.0),
    DistrictMetadata("090713", "Tayacaja", "Salcahuasi", "Red de Salud Tayacaja", 3150, -12.1667, -74.7333, 420, 88.0),
    DistrictMetadata("090714", "Tayacaja", "San Marcos de Rocchac", "Red de Salud Tayacaja", 3182, -12.1500, -74.8833, 350, 86.0),
    DistrictMetadata("090715", "Tayacaja", "Surcubamba", "Red de Salud Tayacaja", 2585, -12.1219, -74.6292, 610, 90.5),
    DistrictMetadata("090716", "Tayacaja", "Tintay Puncu", "Red de Salud Tayacaja", 2350, -12.0833, -74.5333, 590, 91.0),
    DistrictMetadata("090717", "Tayacaja", "Quichuas", "Red de Salud Tayacaja", 3050, -12.4667, -74.7333, 510, 84.0),
    DistrictMetadata("090718", "Tayacaja", "Andaymarca", "Red de Salud Tayacaja", 2850, -12.3333, -74.6500, 390, 85.0),
    DistrictMetadata("090719", "Tayacaja", "Roble", "Red de Salud Tayacaja", 2480, -12.0667, -74.4833, 310, 89.0),
    DistrictMetadata("090720", "Tayacaja", "Pichos", "Red de Salud Tayacaja", 3200, -12.2833, -74.9167, 280, 84.0),
    DistrictMetadata("090721", "Tayacaja", "Santiago de Tucuma", "Red de Salud Tayacaja", 3310, -12.3667, -74.8833, 270, 82.0),
]

SQLITE_DDL = """
CREATE TABLE IF NOT EXISTS cat_ubigeo_hvc (
    ubigeo TEXT PRIMARY KEY,
    provincia TEXT NOT NULL,
    distrito TEXT NOT NULL,
    red_salud TEXT NOT NULL,
    altitud_msnm INTEGER NOT NULL,
    latitud REAL NOT NULL,
    longitud REAL NOT NULL,
    poblacion_menor_5 INTEGER NOT NULL DEFAULT 500,
    ruralidad_pct REAL NOT NULL DEFAULT 65.0
);

CREATE TABLE IF NOT EXISTS registro_cargas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fuente TEXT NOT NULL,
    url_origen TEXT NOT NULL,
    fecha_publicacion_portal TEXT,
    fecha_consulta TEXT NOT NULL,
    hash_sha256 TEXT NOT NULL,
    hubo_cambio INTEGER NOT NULL DEFAULT 1,
    ruta_archivo_crudo TEXT NOT NULL,
    registros_procesados INTEGER NOT NULL DEFAULT 0,
    estado TEXT NOT NULL DEFAULT 'OK',
    detalle_mensaje TEXT
);

CREATE TABLE IF NOT EXISTS serie_historica_distrital (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ubigeo TEXT NOT NULL,
    anio INTEGER NOT NULL,
    semestre INTEGER NOT NULL DEFAULT 2,
    tasa_dci_pct REAL NOT NULL,
    tasa_anemia_pct REAL NOT NULL,
    tasa_bajo_peso_pct REAL NOT NULL,
    ninos_evaluados INTEGER NOT NULL DEFAULT 300,
    pobreza_monetaria_pct REAL NOT NULL,
    educacion_materna_secundaria_pct REAL NOT NULL,
    agua_cloro_adecuado_pct REAL NOT NULL,
    saneamiento_basico_pct REAL NOT NULL,
    controles_cred_completo_pct REAL NOT NULL,
    lactancia_materna_exclusiva_pct REAL NOT NULL,
    ejecucion_pan_mef_pct REAL NOT NULL,
    presupuesto_pan_per_capita_soles REAL NOT NULL,
    cobertura_juntos_pct REAL NOT NULL,
    cobertura_cuna_mas_pct REAL NOT NULL,
    cobertura_qali_warma_pct REAL NOT NULL,
    dias_heladas_anual INTEGER NOT NULL,
    temp_minima_promedio_c REAL NOT NULL,
    precipitacion_anual_mm REAL NOT NULL,
    UNIQUE(ubigeo, anio, semestre),
    FOREIGN KEY (ubigeo) REFERENCES cat_ubigeo_hvc(ubigeo) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS predicciones_dci (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ubigeo TEXT NOT NULL,
    anio_base INTEGER NOT NULL,
    horizonte_proyeccion TEXT NOT NULL DEFAULT 'PROXIMO_SEMESTRE',
    dci_actual_pct REAL NOT NULL,
    dci_proyectada_pct REAL NOT NULL,
    probabilidad_riesgo_critico REAL NOT NULL,
    nivel_riesgo TEXT NOT NULL,
    supera_umbral_algedonico INTEGER NOT NULL,
    valores_shap_json TEXT NOT NULL,
    top_factores_riesgo TEXT NOT NULL,
    version_modelo TEXT NOT NULL DEFAULT 'catboost_shap_v1',
    fecha_prediccion TEXT NOT NULL,
    FOREIGN KEY (ubigeo) REFERENCES cat_ubigeo_hvc(ubigeo) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS alertas_y_recomendaciones_msv (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_prediccion INTEGER,
    ubigeo TEXT NOT NULL,
    provincia TEXT NOT NULL,
    nivel_riesgo TEXT NOT NULL,
    canal_destino TEXT NOT NULL,
    sintesis_narrativa_s4 TEXT NOT NULL,
    recomendacion_salud TEXT NOT NULL,
    recomendacion_agua_saneamiento TEXT NOT NULL,
    recomendacion_agricultura_midis TEXT NOT NULL,
    oei_pei_vinculados TEXT NOT NULL,
    ods_vinculados TEXT NOT NULL,
    proveedor_llm TEXT NOT NULL,
    estado_aprobacion_humana TEXT NOT NULL DEFAULT 'PENDIENTE_APROBACION',
    aprobado_por TEXT,
    fecha_creacion TEXT NOT NULL,
    fecha_resolucion TEXT,
    FOREIGN KEY (ubigeo) REFERENCES cat_ubigeo_hvc(ubigeo) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_serie_anio_ubigeo ON serie_historica_distrital(anio, ubigeo);
CREATE INDEX IF NOT EXISTS idx_pred_ubigeo_id ON predicciones_dci(ubigeo, id DESC);
CREATE INDEX IF NOT EXISTS idx_cargas_fuente_url ON registro_cargas(fuente, url_origen, id DESC);
CREATE INDEX IF NOT EXISTS idx_alertas_ubigeo_id ON alertas_y_recomendaciones_msv(ubigeo, id DESC);
"""


def _create_postgres_connection_factory(pg_url: str) -> Any:
    """Crea un adaptador compatible con DB-API/SQLite sobre psycopg2 para PostgreSQL 16 (Equipo 2)."""
    import psycopg2
    import psycopg2.extras

    dsn = pg_url.replace("postgresql+psycopg2://", "postgresql://")

    class _PgCursorWrapper:
        def __init__(self, cur: Any, lastrowid: int | None = None) -> None:
            self._cur = cur
            self.lastrowid = lastrowid

        def fetchall(self) -> List[Any]:
            return self._cur.fetchall()

        def fetchone(self) -> Any:
            return self._cur.fetchone()

    class _PgConnectionWrapper:
        def __init__(self) -> None:
            self._conn = psycopg2.connect(dsn)

        def __enter__(self) -> "_PgConnectionWrapper":
            return self

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            try:
                if exc_type is not None:
                    self._conn.rollback()
            finally:
                self._conn.close()

        def execute(self, sql: str, params: Tuple[Any, ...] = ()) -> _PgCursorWrapper:
            pg_sql = sql.replace("?", "%s")
            stripped = pg_sql.strip()
            needs_returning = (
                stripped.upper().startswith("INSERT INTO ")
                and "ON CONFLICT" not in stripped.upper()
                and "RETURNING" not in stripped.upper()
            )
            if needs_returning:
                pg_sql = stripped.rstrip(";") + " RETURNING id"
            cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(pg_sql, params)
            lastrowid = None
            if needs_returning:
                row = cur.fetchone()
                if row and "id" in row:
                    lastrowid = int(row["id"])
            return _PgCursorWrapper(cur, lastrowid=lastrowid)

        def executemany(self, sql: str, seq_of_params: List[Tuple[Any, ...]]) -> None:
            pg_sql = sql.replace("?", "%s")
            cur = self._conn.cursor()
            psycopg2.extras.execute_batch(cur, pg_sql, seq_of_params, page_size=250)

        def commit(self) -> None:
            self._conn.commit()

    return _PgConnectionWrapper


def create_db_engine_and_session(database_url: str | None = None) -> Tuple[str, Any]:
    """
    Inicializa el almacenamiento relacional y asegura la carga semilla de los 100 distritos
    de las 7 provincias de Huancavelica. Soporta tanto PostgreSQL 16 (Equipo 2) como SQLite WAL (Equipo 1).
    """
    url = database_url or os.getenv("DATABASE_URL", "sqlite:///./data/sentinelnutri_dev.db")
    if url.startswith("postgresql"):
        pg_factory = _create_postgres_connection_factory(url)
        with pg_factory() as conn:
            conn.executemany(
                """
                INSERT INTO cat_ubigeo_hvc (
                    ubigeo, provincia, distrito, red_salud, altitud_msnm,
                    latitud, longitud, poblacion_menor_5, ruralidad_pct
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (ubigeo) DO NOTHING
                """,
                [
                    (
                        d.ubigeo,
                        d.provincia,
                        d.distrito,
                        d.red_salud,
                        d.altitud_msnm,
                        d.latitud,
                        d.longitud,
                        d.poblacion_menor_5,
                        d.ruralidad_pct,
                    )
                    for d in DEFAULT_HUANCAVELICA_DISTRICTS
                ],
            )
            conn.commit()
        return url, pg_factory

    if url.startswith("sqlite:///"):
        db_file = url.replace("sqlite:///", "")
        if db_file != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(db_file)), exist_ok=True)
    else:
        db_file = "./data/sentinelnutri_dev.db"
        os.makedirs(os.path.dirname(os.path.abspath(db_file)), exist_ok=True)

    def get_connection() -> sqlite3.Connection:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA temp_store = MEMORY;")
        return conn

    with get_connection() as conn:
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.executescript(SQLITE_DDL)
        conn.executemany(
            """
            INSERT OR IGNORE INTO cat_ubigeo_hvc (
                ubigeo, provincia, distrito, red_salud, altitud_msnm,
                latitud, longitud, poblacion_menor_5, ruralidad_pct
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    d.ubigeo,
                    d.provincia,
                    d.distrito,
                    d.red_salud,
                    d.altitud_msnm,
                    d.latitud,
                    d.longitud,
                    d.poblacion_menor_5,
                    d.ruralidad_pct,
                )
                for d in DEFAULT_HUANCAVELICA_DISTRICTS
            ],
        )
        conn.commit()

    return db_file, get_connection
