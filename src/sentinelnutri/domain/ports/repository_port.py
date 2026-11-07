"""Puerto de Persistencia para Series Históricas, Registro de Cargas y Alertas MSV."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from sentinelnutri.domain.entities.alert_msv import ApprovalStatus, MSVAlertReport
from sentinelnutri.domain.entities.district import DistrictIndicatorRecord, DistrictMetadata
from sentinelnutri.domain.entities.prediction import DistrictRiskPrediction


class RepositoryPort(ABC):
    """Contrato de acceso a datos desacoplado del motor relacional (PostgreSQL / SQLite)."""

    @abstractmethod
    def get_all_districts(self) -> List[DistrictMetadata]:
        """Devuelve el catálogo de distritos monitoreados de Huancavelica."""

    @abstractmethod
    def get_latest_load_hash(self, fuente: str, url_origen: str) -> Optional[str]:
        """Obtiene el último hash SHA-256 registrado para una fuente y URL."""

    @abstractmethod
    def register_load_attempt(
        self,
        fuente: str,
        url_origen: str,
        hash_sha256: str,
        hubo_cambio: bool,
        ruta_archivo_crudo: str,
        registros_procesados: int,
        estado: str = "OK",
        detalle_mensaje: str = "",
    ) -> Dict[str, object]:
        """Registra un evento de control de carga en `registro_cargas`."""

    @abstractmethod
    def upsert_historical_records(self, records: List[DistrictIndicatorRecord]) -> int:
        """Inserta o actualiza registros en `serie_historica_distrital` por ubigeo y periodo."""

    @abstractmethod
    def get_historical_series(
        self,
        ubigeo: Optional[str] = None,
        anio_inicio: int = 2014,
        anio_fin: int = 2025,
    ) -> List[DistrictIndicatorRecord]:
        """Consulta la serie histórica distrital filtrada por ubigeo y rango de años."""

    @abstractmethod
    def save_prediction(self, prediction: DistrictRiskPrediction) -> int:
        """Guarda una predicción del motor CatBoost+SHAP y devuelve su ID."""

    @abstractmethod
    def get_latest_predictions(self, provincia: Optional[str] = None) -> List[DistrictRiskPrediction]:
        """Devuelve las predicciones más recientes por distrito."""

    @abstractmethod
    def save_alert_report(self, report: MSVAlertReport) -> int:
        """Guarda un informe del módulo agéntico y su estado de aprobación humana."""

    @abstractmethod
    def update_alert_approval(
        self,
        alert_id: int,
        status: ApprovalStatus,
        approved_by: str,
    ) -> Optional[MSVAlertReport]:
        """Actualiza el estado de aprobación humana (HITL) de una recomendación."""

