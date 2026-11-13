"""
Herramienta 3 del Agente Supervisor: `predecir_riesgo` (Tabla 5).
Calcula el índice de riesgo de DCI por distrito usando el motor CatBoost (/predict)
y evalúa de manera determinista la Regla Fija del umbral algedónico (DCI proyectada > 25% -> S5).
"""

from typing import Dict, List, Optional
from sentinelnutri.domain.ports.predictor_port import PredictorPort
from sentinelnutri.domain.ports.repository_port import RepositoryPort
from sentinelnutri.domain.rules.fixed_thresholds import (
    ALGEDONIC_DCI_THRESHOLD_PCT,
    evaluate_fixed_algedonic_rule,
)


class Tool3PredecirRiesgoUseCase:
    """Caso de uso del Atenuador de Variedad Ambiental (CatBoost /predict + Regla Fija Algedónica)."""

    def __init__(
        self,
        repository: RepositoryPort,
        predictor: PredictorPort,
        algedonic_threshold_pct: float = ALGEDONIC_DCI_THRESHOLD_PCT,
    ) -> None:
        self._repo = repository
        self._predictor = predictor
        self._threshold = algedonic_threshold_pct

    def execute(self, ubigeo: Optional[str] = None, anio_corte: int = 2024) -> Dict[str, object]:
        """
        Ejecuta el modelo CatBoost sobre el corte más reciente de cada distrito de Huancavelica,
        persiste las predicciones en PostgreSQL y separa los distritos que activan el canal algedónico S5.
        """
        records = self._repo.get_historical_series(
            ubigeo=ubigeo,
            anio_inicio=anio_corte,
            anio_fin=anio_corte,
        )
        if not records:
            # Si aún no hay corte del año solicitado, toma el último disponible en BD
            all_records = self._repo.get_historical_series(ubigeo=ubigeo, anio_inicio=2014, anio_fin=2025)
            latest_by_ubigeo = {}
            for rec in all_records:
                key = rec.ubigeo
                if key not in latest_by_ubigeo or (rec.anio, rec.semestre) > (
                    latest_by_ubigeo[key].anio,
                    latest_by_ubigeo[key].semestre,
                ):
                    latest_by_ubigeo[key] = rec
            records = list(latest_by_ubigeo.values())

        predictions_out: List[Dict[str, object]] = []
        algedonic_districts: List[Dict[str, object]] = []

        for rec in records:
            pred = self._predictor.predict_district_risk(rec)
            # REGLA FIJA 2: Evaluación determinista del umbral algedónico (fuera del alcance del LLM)
            route_decision = evaluate_fixed_algedonic_rule(
                ubigeo=pred.ubigeo,
                dci_proyectada_pct=pred.dci_proyectada_pct,
                threshold_pct=self._threshold,
            )
            pred.supera_umbral_algedonico = route_decision.supera_umbral_critico
            pred_id = self._repo.save_prediction(pred)

            item = {
                "id_prediccion": pred_id,
                "ubigeo": pred.ubigeo,
                "provincia": pred.provincia,
                "distrito": pred.distrito,
                "red_salud": pred.red_salud,
                "anio_base": pred.anio_base,
                "dci_actual_pct": round(pred.dci_actual_pct, 2),
                "dci_proyectada_pct": round(pred.dci_proyectada_pct, 2),
                "probabilidad_riesgo_critico": round(pred.probabilidad_riesgo_critico, 4),
                "nivel_riesgo": pred.nivel_riesgo.value,
                "supera_umbral_algedonico_25pct": route_decision.supera_umbral_critico,
                "canal_msv_asignado": route_decision.canal_obligatorio.value,
                "top_factores_shap": [
                    {
                        "variable": c.variable,
                        "etiqueta": c.etiqueta_legible,
                        "valor_shap": round(c.valor_shap, 4),
                        "efecto": c.direccion_impacto,
                    }
                    for c in pred.top_contribuciones_shap[:4]
                ],
            }
            predictions_out.append(item)
            if route_decision.supera_umbral_critico:
                algedonic_districts.append(item)

        predictions_out.sort(key=lambda x: float(x["dci_proyectada_pct"]), reverse=True)

        return {
            "tool": "predecir_riesgo",
            "motor": "CatBoost + SHAP (Atenuador de Variedad Ambiental)",
            "umbral_algedonico_fijo_pct": self._threshold,
            "total_distritos_evaluados": len(predictions_out),
            "total_alertas_algedonicas_s5": len(algedonic_districts),
            "activar_canal_algedonico_s5": len(algedonic_districts) > 0,
            "distritos_criticos_s5": algedonic_districts,
            "predicciones_distritales": predictions_out,
        }

