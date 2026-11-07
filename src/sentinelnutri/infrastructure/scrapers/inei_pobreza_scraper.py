"""
Scraper de INEI (Censos Nacionales y Mapa de Pobreza Distrital):
Obtiene tasas de pobreza monetaria, necesidades básicas insatisfechas (NBI), ruralidad y población por distrito.
"""

from .base_ethical_scraper import EthicalWebScraperClient


class IneiPobrezaScraper:
    """Extractor de tablas plurianuales de pobreza y ruralidad distrital del INEI."""

    PORTAL_URL = "https://www.inei.gob.pe/estadisticas/indice-tematico/social/"

    def __init__(self, client: EthicalWebScraperClient | None = None) -> None:
        self.client = client or EthicalWebScraperClient()

