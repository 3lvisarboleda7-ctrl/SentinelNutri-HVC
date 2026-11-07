"""Puerto del Motor Predictivo Explicable (CatBoost + SHAP)."""

from abc import ABC, abstractmethod
from typing import Dict, List
from sentinelnutri.domain.entities.district import DistrictIndicatorRecord
from sentinelnutri.domain.entities.prediction import DistrictRiskPrediction


class PredictorPort(ABC):
    """Contrato para el entrenamiento, inferencia y explicabilidad SHAP por distrito."""

    @abstractmethod
    def train_and_evaluate(self, records: List[DistrictIndicatorRecord]) -> Dict[str, object]:
        """Entrena el modelo con validación cruzada estratificada y devuelve métricas (AUC, F1, precisión)."""

    @abstractmethod
    def predict_district_risk(self, record: DistrictIndicatorRecord) -> DistrictRiskPrediction:
        """Calcula el riesgo proyectado de DCI y las contribuciones SHAP para un distrito."""

