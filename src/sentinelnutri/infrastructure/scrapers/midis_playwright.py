"""
Scraper 5 — MIDIS con Playwright (REDinforma / InfoMIDIS):
Extrae la cobertura mensual y anual por distrito de los programas sociales adscritos al MIDIS
en las 7 provincias de Huancavelica: Juntos, Cuna Más y Qali Warma (2014–2024).
"""

import csv
import io
import re
from typing import Any, Dict, List, Optional

from sentinelnutri.infrastructure.etl.ubigeo_harmonizer import (
    normalize_ubigeo_code,
    resolve_ubigeo_by_name,
)
from .base_ethical_scraper import EthicalWebScraperClient


class MidisPlaywrightScraper:
    """Controlador Playwright para los tableros dinámicos de cobertura del MIDIS (REDinforma)."""

    PORTAL_URL = "https://sdv.midis.gob.pe/redinforma/"

    def __init__(self, client: Optional[EthicalWebScraperClient] = None) -> None:
        self.client = client or EthicalWebScraperClient()

    async def scrape_midis_dashboard_html(self) -> str:
        """Extrae el DOM renderizado del tablero de programas sociales del MIDIS."""
        return await self.client.fetch_dynamic_page_with_playwright(self.PORTAL_URL)

    def parse_midis_csv_or_html(self, raw_content: str, year: int = 2024) -> List[Dict[str, Any]]:
        """
        Procesa exportaciones CSV o tablas HTML de cobertura distrital de Juntos, Cuna Más y Qali Warma.
        """
        results: List[Dict[str, Any]] = []
        if "ubigeo" in raw_content.lower() and "," in raw_content:
            reader = csv.DictReader(io.StringIO(raw_content))
            for row in reader:
                norm = {str(k or "").strip().lower(): str(v or "").strip() for k, v in row.items()}
                ubigeo = normalize_ubigeo_code(norm.get("ubigeo")) or resolve_ubigeo_by_name(norm.get("distrito", ""))
                if not ubigeo:
                    continue
                results.append(
                    {
                        "ubigeo": ubigeo,
                        "anio": int(norm.get("anio") or year),
                        "cobertura_juntos_pct": float(norm.get("cobertura_juntos_pct") or 0.0),
                        "cobertura_cuna_mas_pct": float(norm.get("cobertura_cuna_mas_pct") or 0.0),
                        "cobertura_qali_warma_pct": float(norm.get("cobertura_qali_warma_pct") or 0.0),
                    }
                )
            return results

        row_pattern = re.compile(
            r"(09\d{4})\s*</td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>([\d\.]+)</td>\s*<td[^>]*>([\d\.]+)</td>\s*<td[^>]*>([\d\.]+)</td>",
            re.IGNORECASE,
        )
        for match in row_pattern.finditer(raw_content):
            results.append(
                {
                    "ubigeo": match.group(1),
                    "anio": year,
                    "cobertura_juntos_pct": float(match.group(3)),
                    "cobertura_cuna_mas_pct": float(match.group(4)),
                    "cobertura_qali_warma_pct": float(match.group(5)),
                }
            )
        return results
