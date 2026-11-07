"""
Scraper 3 — INEI (Censos Nacionales y Mapa de Pobreza Monetaria Distrital):
Obtiene tasas de pobreza monetaria, necesidades básicas insatisfechas (NBI), ruralidad y población
menor de 5 años para los 100 distritos de las 7 provincias de Huancavelica.
"""

import csv
import io
from typing import Any, Dict, List, Optional

from sentinelnutri.infrastructure.etl.ubigeo_harmonizer import (
    normalize_ubigeo_code,
    resolve_ubigeo_by_name,
)
from .base_ethical_scraper import EthicalWebScraperClient


class IneiPobrezaScraper:
    """Extractor de tablas plurianuales de pobreza monetaria y ruralidad distrital del INEI."""

    PORTAL_URL = "https://www.inei.gob.pe/estadisticas/indice-tematico/social/"

    def __init__(self, client: Optional[EthicalWebScraperClient] = None) -> None:
        self.client = client or EthicalWebScraperClient()

    def parse_pobreza_csv_bytes(self, csv_bytes: bytes, default_year: int = 2024) -> List[Dict[str, Any]]:
        """Extrae indicadores socioeconómicos distritales de Huancavelica (09xxxx)."""
        text = csv_bytes.decode("utf-8", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        rows: List[Dict[str, Any]] = []
        for row in reader:
            norm = {str(k or "").strip().lower(): str(v or "").strip() for k, v in row.items()}
            ubigeo = normalize_ubigeo_code(norm.get("ubigeo")) or resolve_ubigeo_by_name(
                norm.get("distrito", ""),
                norm.get("provincia", ""),
            )
            if not ubigeo:
                continue
            rows.append(
                {
                    "ubigeo": ubigeo,
                    "anio": int(norm.get("anio") or default_year),
                    "pobreza_monetaria_pct": float(norm.get("pobreza_monetaria_pct") or norm.get("pobreza_pct") or 0.0),
                    "ruralidad_pct": float(norm.get("ruralidad_pct") or 0.0),
                    "poblacion_menor_5": int(float(norm.get("poblacion_menor_5") or 500)),
                }
            )
        return rows
