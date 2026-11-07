"""Entidades de Distrito e Indicadores Multidimensionales (Huancavelica - Ubigeo 09xxxx)."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DistrictMetadata:
    """Metadatos territoriales y de coordinación (S1 / S2) de un distrito de Huancavelica."""

    ubigeo: str
    provincia: str
    distrito: str
    red_salud: str
    altitud_msnm: int
    latitud: float
    longitud: float
    poblacion_menor_5: int = 500
    ruralidad_pct: float = 65.0


@dataclass
class DistrictIndicatorRecord:
    """Registro histórico integrado por ubigeo distrital (5 dimensiones del modelo predictivo)."""

    ubigeo: str
    anio: int
    semestre: int
    # 1. Antropométrica y Nutricional (SIEN-HIS INS/CENAN)
    tasa_dci_pct: float
    tasa_anemia_pct: float
    tasa_bajo_peso_pct: float
    ninos_evaluados: int
    # 2. Socioeconómica (INEI Censos y Mapa de Pobreza / ENDES)
    pobreza_monetaria_pct: float
    educacion_materna_secundaria_pct: float
    # 3. Acceso a Servicios (ENDES / INEI)
    agua_cloro_adecuado_pct: float
    saneamiento_basico_pct: float
    controles_cred_completo_pct: float
    lactancia_materna_exclusiva_pct: float
    # 4. Agroalimentaria, Presupuesto y Programas Sociales (MEF Consulta Amigable + MIDIS)
    ejecucion_pan_mef_pct: float
    presupuesto_pan_per_capita_soles: float
    cobertura_juntos_pct: float
    cobertura_cuna_mas_pct: float
    cobertura_qali_warma_pct: float
    # 5. Climática (SENAMHI)
    dias_heladas_anual: int
    temp_minima_promedio_c: float
    precipitacion_anual_mm: float
    provincia: Optional[str] = None
    distrito: Optional[str] = None
    red_salud: Optional[str] = None
    altitud_msnm: Optional[int] = None
    ruralidad_pct: Optional[float] = None

