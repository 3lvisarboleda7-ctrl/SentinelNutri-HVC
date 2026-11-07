"""
Scraper de SENAMHI (Clima y Heladas en Huancavelica):
Consulta datos diarios y mensuales de heladas, temperatura mínima y precipitación de las estaciones
meteorológicas de Huancavelica.
"""

from .base_ethical_scraper import EthicalWebScraperClient


class SenamhiScraper:
    """Extractor de series meteorológicas y días de heladas del SENAMHI."""

    PORTAL_URL = "https://www.senamhi.gob.pe/?p=estaciones"

    def __init__(self, client: EthicalWebScraperClient | None = None) -> None:
        self.client = client or EthicalWebScraperClient()

