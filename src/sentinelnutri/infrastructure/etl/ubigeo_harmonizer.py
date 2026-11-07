"""
Módulo de Armonización e Integración por Ubigeo Distrital (090101 al 090721 - Huancavelica).

Normaliza códigos de 5 o 6 dígitos (ej. `90101` -> `090101`) y resuelve nombres de distritos
provenientes de reportes PDF/CSV/HTML (SIEN-HIS, INEI, MEF, MIDIS, SENAMHI) hacia su código
oficial INEI de 6 dígitos en las 7 provincias de Huancavelica.
"""

from typing import Dict, List, Optional
import unicodedata

from sentinelnutri.domain.entities.district import DistrictIndicatorRecord
from sentinelnutri.infrastructure.persistence.database import DEFAULT_HUANCAVELICA_DISTRICTS


def _strip_accents_upper(text: str) -> str:
    clean = unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode("ascii")
    return " ".join(clean.upper().replace("-", " ").split())


_DISTRICT_NAME_TO_UBIGEO: Dict[str, str] = {
    _strip_accents_upper(d.distrito): d.ubigeo for d in DEFAULT_HUANCAVELICA_DISTRICTS
}

_PROVINCE_DISTRICT_TO_UBIGEO: Dict[tuple[str, str], str] = {
    (_strip_accents_upper(d.provincia), _strip_accents_upper(d.distrito)): d.ubigeo
    for d in DEFAULT_HUANCAVELICA_DISTRICTS
}


def normalize_ubigeo_code(raw_code: object) -> Optional[str]:
    """Convierte códigos numéricos o texto (`90101` o `090101`) al formato oficial `09xxxx`."""
    digits = "".join(ch for ch in str(raw_code or "").strip() if ch.isdigit())
    if len(digits) == 5 and digits.startswith("9"):
        digits = "0" + digits
    if len(digits) == 6 and digits.startswith("09"):
        return digits
    return None


def resolve_ubigeo_by_name(distrito: str, provincia: Optional[str] = None) -> Optional[str]:
    """Resuelve el código de ubigeo oficial a partir del nombre del distrito (y provincia opcional)."""
    dist_norm = _strip_accents_upper(distrito)
    if provincia:
        prov_norm = _strip_accents_upper(provincia)
        match = _PROVINCE_DISTRICT_TO_UBIGEO.get((prov_norm, dist_norm))
        if match:
            return match
    return _DISTRICT_NAME_TO_UBIGEO.get(dist_norm)


def filter_valid_huancavelica_ubigeos(records: List[DistrictIndicatorRecord]) -> List[DistrictIndicatorRecord]:
    """Garantiza que todos los registros pertenezcan al departamento de Huancavelica (prefijo '09')."""
    return [r for r in records if str(r.ubigeo).startswith("09") and len(str(r.ubigeo)) == 6]
