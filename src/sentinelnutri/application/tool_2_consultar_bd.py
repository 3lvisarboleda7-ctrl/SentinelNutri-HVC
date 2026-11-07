"""
Herramienta 2 del Agente Supervisor: `consultar_bd` (Tabla 5).
Lee las series históricas por distrito (2014-2024+) y el registro de cargas desde PostgreSQL.
"""

from dataclasses import asdict
from typing import Dict, Optional
from sentinelnutri.domain.ports.repository_port import RepositoryPort


class Tool2ConsultarBdUseCase:
    """Caso de uso para consultar series históricas distritales y estado de cargas en PostgreSQL."""

    def __init__(self, repository: RepositoryPort) -> None:
        self._repo = repository

    def execute(
        self,
        ubigeo: Optional[str] = None,
        anio_inicio: int = 2014,
        anio_fin: int = 2024,
    ) -> Dict[str, object]:
        """Devuelve la serie histórica multidimensional y metadatos territoriales."""
        districts = self._repo.get_all_districts()
        series = self._repo.get_historical_series(
            ubigeo=ubigeo,
            anio_inicio=anio_inicio,
            anio_fin=anio_fin,
        )

        return {
            "tool": "consultar_bd",
            "filtro_ubigeo": ubigeo or "TODOS_LOS_DISTRITOS_HVC",
            "rango_anios": f"{anio_inicio}-{anio_fin}",
            "total_distritos_catalogo": len(districts),
            "total_registros_serie": len(series),
            "registros": [asdict(record) for record in series[:50]],
        }

