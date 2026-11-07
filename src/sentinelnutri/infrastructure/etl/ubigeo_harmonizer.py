"""Módulo de Armonización e Integración por Ubigeo Distrital (09xxxx)."""

from typing import List
from sentinelnutri.domain.entities.district import DistrictIndicatorRecord


def filter_valid_huancavelica_ubigeos(records: List[DistrictIndicatorRecord]) -> List[DistrictIndicatorRecord]:
    """Garantiza que todos los registros pertenezcan al departamento de Huancavelica (prefijo '09')."""
    return [r for r in records if str(r.ubigeo).startswith("09") and len(str(r.ubigeo)) == 6]

