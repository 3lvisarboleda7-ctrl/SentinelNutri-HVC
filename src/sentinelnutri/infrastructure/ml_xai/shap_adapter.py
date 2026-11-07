"""
Adaptador de Explicabilidad SHAP (TreeExplainer) para Soporte a la Función de Auditoría S3* del MSV.
"""

from typing import Dict, List
from sentinelnutri.domain.entities.prediction import ShapContribution


def format_shap_audit_summary(ubigeo: str, distrito: str, contributions: List[ShapContribution]) -> Dict[str, object]:
    """Formatea las contribuciones SHAP locales para auditoría de confianza en el sector público (S3*)."""
    positive_drivers = [c for c in contributions if c.valor_shap > 0]
    protective_drivers = [c for c in contributions if c.valor_shap <= 0]

    return {
        "ubigeo": ubigeo,
        "distrito": distrito,
        "factores_que_incrementan_riesgo": [
            {"variable": c.variable, "determinante": c.etiqueta_legible, "shap_pts": round(c.valor_shap, 4)}
            for c in positive_drivers
        ],
        "factores_protectores_o_atenuantes": [
            {"variable": c.variable, "determinante": c.etiqueta_legible, "shap_pts": round(c.valor_shap, 4)}
            for c in protective_drivers
        ],
    }

