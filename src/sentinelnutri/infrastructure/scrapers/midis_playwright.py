"""
Scraper Dinámico con Playwright para MIDIS (REDinforma / InfoMIDIS):
Extrae la cobertura mensual por distrito de los programas sociales Juntos, Cuna Más y Qali Warma en Huancavelica.
"""

from .base_ethical_scraper import EthicalWebScraperClient


class MidisPlaywrightScraper:
    """Controlador Playwright para los tableros dinámicos de cobertura del MIDIS."""

    PORTAL_URL = "https://sdv.midis.gob.pe/redinforma/"

    def __init__(self, client: EthicalWebScraperClient | None = None) -> None:
        self.client = client or EthicalWebScraperClient()

    async def scrape_midis_dashboard_html(self) -> str:
        """Extrae el DOM renderizado del tablero de programas sociales del MIDIS."""
        return await self.client.fetch_dynamic_page_with_playwright(self.PORTAL_URL)

