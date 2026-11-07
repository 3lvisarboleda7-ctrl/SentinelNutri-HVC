"""
Scraper 4 — MEF Consulta Amigable con Playwright (Categoría Presupuestal 0001: Programa Articulado Nutricional):
Navega los formularios dinámicos ASP.NET del Ministerio de Economía y Finanzas (`apps5.mineco.gob.pe`)
para extraer el PIM, Devengado y % de Avance de ejecución presupuestal del PAN (0001) en los
100 gobiernos locales de Huancavelica (Departamento 09, serie 2014–2024).
"""

import re
from typing import Any, Dict, List, Optional

from sentinelnutri.infrastructure.etl.ubigeo_harmonizer import (
    normalize_ubigeo_code,
    resolve_ubigeo_by_name,
)
from .base_ethical_scraper import EthicalWebScraperClient


class MefPanPlaywrightScraper:
    """Controlador Playwright para Consulta Amigable del MEF (Categoría Presupuestal 0001 - Huancavelica)."""

    PORTAL_URL = "https://apps5.mineco.gob.pe/transparencia/Navegador/default.aspx"
    CATEGORY_PAN_CODE = "0001"
    DEPARTMENT_HVC_CODE = "09"

    def __init__(self, client: Optional[EthicalWebScraperClient] = None) -> None:
        self.client = client or EthicalWebScraperClient()

    async def scrape_pan_execution_html(self, year: int = 2024) -> str:
        """
        Navega con Playwright hacia el año solicitado en Consulta Amigable del MEF,
        seleccionando Categoría Presupuestal 0001 (PAN) y Departamento 09 (Huancavelica).
        """
        target = f"{self.PORTAL_URL}?y={year}&ap=Programa"
        return await self.client.fetch_dynamic_page_with_playwright(
            target,
            wait_selector="table.Data",
        )

    def parse_mef_html_table(self, html_content: str, year: int = 2024) -> List[Dict[str, Any]]:
        """
        Extrae de la tabla HTML de Consulta Amigable las filas de municipalidades distritales de Huancavelica:
        Código/Municipalidad, PIA, PIM, Devengado y % de Avance del Programa Articulado Nutricional (0001).
        """
        results: List[Dict[str, Any]] = []
        row_pattern = re.compile(
            r"<tr[^>]*>.*?<td[^>]*>\s*(?:30\d{4}|09\d{4})?\s*[:\-]?\s*([A-Za-zÁÉÍÓÚÑáéíóúñ\s\-\.]+?)</td>"
            r".*?<td[^>]*>\s*([\d,\.]+)\s*</td>"  # PIM
            r".*?<td[^>]*>\s*([\d,\.]+)\s*</td>"  # Devengado
            r".*?<td[^>]*>\s*(\d+(?:[\.,]\d+)?)\s*</td>.*?</tr>",
            re.IGNORECASE | re.DOTALL,
        )
        for match in row_pattern.finditer(html_content):
            raw_name = match.group(1).strip()
            ubigeo = normalize_ubigeo_code(raw_name) or resolve_ubigeo_by_name(raw_name)
            if not ubigeo:
                continue
            pim_soles = float(match.group(2).replace(",", ""))
            devengado_soles = float(match.group(3).replace(",", ""))
            avance_pct = float(match.group(4).replace(",", "."))
            results.append(
                {
                    "ubigeo": ubigeo,
                    "anio": year,
                    "pim_pan_soles": pim_soles,
                    "devengado_pan_soles": devengado_soles,
                    "ejecucion_pan_mef_pct": round(avance_pct, 2),
                }
            )
        return results
