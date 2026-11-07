"""Entidades de Predicción de Riesgo de DCI y Explicabilidad XAI (SHAP)."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class RiskLevel(str, Enum):
    """Niveles de riesgo nutricional distrital para el Sistema 4."""

    BAJO = "BAJO"
    MODERADO = "MODERADO"
    ALTO = "ALTO"
    CRITICO = "CRITICO"


@dataclass(frozen=True)
class ShapContribution:
    """Contribución local de una variable según valores SHAP (Soporte a Auditoría S3*)."""

    variable: str
    etiqueta_legible: str
    valor_observado: float
    valor_shap: float
    direccion_impacto: str  # "INCREMENTA_RIESGO" o "ATENUA_RIESGO"


@dataclass
class DistrictRiskPrediction:
    """Resultado del Atenuador de Variedad Ambiental (Motor CatBoost + SHAP)."""

    ubigeo: str
    provincia: str
    distrito: str
    red_salud: str
    anio_base: int
    dci_actual_pct: float
    dci_proyectada_pct: float
    probabilidad_riesgo_critico: float
    nivel_riesgo: RiskLevel
    supera_umbral_algedonico: bool
    valores_shap: Dict[str, float] = field(default_factory=dict)
    top_contribuciones_shap: List[ShapContribution] = field(default_factory=list)
    version_modelo: str = "catboost_shap_v1"

