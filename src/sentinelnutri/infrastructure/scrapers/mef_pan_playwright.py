"""
Scraper Dinámico con Playwright para MEF (Consulta Amigable):
Navega los formularios dinámicos del Ministerio de Economía y Finanzas para extraer
la ejecución mensual del gasto (PIM, Devengado, % Avance) del Programa Articulado Nutricional (0001)
en los gobiernos locales de Huancavelica.
"""

from .base_ethical_scraper import EthicalWebScraperClient


class MefPanPlaywrightScraper:
    """Controlador Playwright para Consulta Amigable del MEF (Categoría Presupuestal 0001)."""

    PORTAL_URL = "https://apps5.mineco.gob.pe/transparencia/Navegador/default.aspx"

    def __init__(self, client: EthicalWebScraperClient | None = None) -> None:
        self.client = client or EthicalWebScraperClient()

    async def scrape_pan_execution_html(self, year: int = 2024) -> str:
        """Navega con Playwright hacia el año solicitado en Consulta Amigable del MEF."""
        target = f"{self.PORTAL_URL}?y={year}&ap=Programa"
        return await self.client.fetch_dynamic_page_with_playwright(target)

