"""
Herramienta 4 del Agente Supervisor: `explicar_riesgo` (Tabla 5).
Identifica las variables que explican el riesgo de cada distrito mediante valores SHAP (XAI),
dando soporte directo a la función de Auditoría (S3*) del MSV (Clavijo, 2026; Navarro-Guillén et al., 2026).
"""

from typing import Dict
from sentinelnutri.domain.ports.predictor_port import PredictorPort
from sentinelnutri.domain.ports.repository_port import RepositoryPort


class Tool4ExplicarRiesgoUseCase:
    """Caso de uso de Explicabilidad XAI (SHAP local por distrito para S3*)."""

    def __init__(self, repository: RepositoryPort, predictor: PredictorPort) -> None:
        self._repo = repository
        self._predictor = predictor

    def execute(self, ubigeo: str) -> Dict[str, object]:
        """Calcula y detalla el desglose de contribuciones SHAP para un ubigeo específico."""
        series = self._repo.get_historical_series(ubigeo=ubigeo, anio_inicio=2014, anio_fin=2025)
        if not series:
            raise ValueError(f"No existen registros históricos para el ubigeo '{ubigeo}'.")

        latest_record = sorted(series, key=lambda r: (r.anio, r.semestre))[-1]
        prediction = self._predictor.predict_district_risk(latest_record)

        return {
            "tool": "explicar_riesgo",
            "funcion_msv": "S3* (Auditoría mediante Explicabilidad XAI - SHAP)",
            "ubigeo": prediction.ubigeo,
            "provincia": prediction.provincia,
            "distrito": prediction.distrito,
            "red_salud": prediction.red_salud,
            "dci_actual_pct": round(prediction.dci_actual_pct, 2),
            "dci_proyectada_pct": round(prediction.dci_proyectada_pct, 2),
            "nivel_riesgo": prediction.nivel_riesgo.value,
            "supera_umbral_algedonico": prediction.supera_umbral_algedonico,
            "contribuciones_shap_ordenadas": [
                {
                    "variable": c.variable,
                    "determinante": c.etiqueta_legible,
                    "valor_distrital_observado": round(c.valor_observado, 2),
                    "aporte_shap_puntos_pct": round(c.valor_shap, 4),
                    "efecto": c.direccion_impacto,
                }
                for c in prediction.top_contribuciones_shap
            ],
            "valores_shap_completos": {k: round(v, 4) for k, v in prediction.valores_shap.items()},
        }

