"""
Scraper 2 — Microdatos ENDES (INEI):
Descarga y procesa módulos anuales de agua segura (cloro residual adecuado), saneamiento básico,
educación materna, lactancia materna exclusiva y controles CRED completos en Huancavelica (Departamento 09).

Soporta lectura de archivos SPSS (`.sav`) mediante `pyreadstat` y tablas CSV agregadas.
"""

import csv
import io
from typing import Any, Dict, List, Optional

from sentinelnutri.infrastructure.etl.ubigeo_harmonizer import (
    normalize_ubigeo_code,
    resolve_ubigeo_by_name,
)
from .base_ethical_scraper import EthicalWebScraperClient


class EndesIneiScraper:
    """Extractor especializado para microdatos ENDES del portal del INEI (Departamento 09)."""

    PORTAL_URL = "https://proyectos.inei.gob.pe/microdatos/"

    def __init__(self, client: Optional[EthicalWebScraperClient] = None) -> None:
        self.client = client or EthicalWebScraperClient()

    def read_sav_file(self, sav_path: str) -> List[Dict[str, Any]]:
        """Lee un archivo de microdatos `.sav` usando `pyreadstat` filtrando el departamento 09 (Huancavelica)."""
        try:
            import pyreadstat

            df, _ = pyreadstat.read_sav(sav_path)
            records = df.to_dict(orient="records")
            filtered: List[Dict[str, Any]] = []
            for rec in records:
                ubigeo = normalize_ubigeo_code(rec.get("UBIGEO") or rec.get("HV024") or rec.get("ubigeo"))
                if ubigeo and ubigeo.startswith("09"):
                    filtered.append(rec)
            return filtered[:500]
        except Exception:
            return []

    def parse_endes_csv_bytes(self, csv_bytes: bytes, default_year: int = 2024) -> List[Dict[str, Any]]:
        """Procesa indicadores de salud materno-infantil y agua/saneamiento de ENDES por ubigeo."""
        text = csv_bytes.decode("utf-8", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        rows: List[Dict[str, Any]] = []
        for row in reader:
            norm = {str(k or "").strip().lower(): str(v or "").strip() for k, v in row.items()}
            ubigeo = normalize_ubigeo_code(norm.get("ubigeo")) or resolve_ubigeo_by_name(norm.get("distrito", ""))
            if not ubigeo:
                continue
            rows.append(
                {
                    "ubigeo": ubigeo,
                    "anio": int(norm.get("anio") or default_year),
                    "agua_cloro_adecuado_pct": float(norm.get("agua_cloro_adecuado_pct") or 0.0),
                    "saneamiento_basico_pct": float(norm.get("saneamiento_basico_pct") or 0.0),
                    "educacion_materna_secundaria_pct": float(norm.get("educacion_materna_secundaria_pct") or 0.0),
                    "controles_cred_completo_pct": float(norm.get("controles_cred_completo_pct") or 0.0),
                    "lactancia_materna_exclusiva_pct": float(norm.get("lactancia_materna_exclusiva_pct") or 0.0),
                }
            )
        return rows
