"""Puerto de Extracción Automatizada para las Fuentes Públicas (Tabla 4 del Proyecto)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from sentinelnutri.domain.entities.district import DistrictIndicatorRecord


@dataclass
class ScrapeResult:
    """Resultado estandarizado de la consulta a un portal público."""

    fuente: str
    url_origen: str
    fecha_publicacion: str
    hash_sha256: str
    hubo_cambio: bool
    ruta_archivo_crudo: str
    registros_extraidos: int
    estado: str  # "OK", "SIN_CAMBIOS", "ERROR_DISENO_PORTAL"
    mensaje: str


class ScraperPort(ABC):
    """Contrato que implementan todos los scrapers estáticos y dinámicos (Playwright)."""

    @abstractmethod
    def execute_extraction(
        self,
        mode: str = "weekly_watch",
        start_year: int = 2014,
        end_year: int = 2024,
    ) -> List[ScrapeResult]:
        """Ejecuta la extracción en modo 'backfill' (2014-2024) o 'weekly_watch'."""

    @abstractmethod
    def build_integrated_records(
        self,
        start_year: int = 2014,
        end_year: int = 2024,
    ) -> List[DistrictIndicatorRecord]:
        """Integra las fuentes descargadas mediante el ubigeo distrital."""

