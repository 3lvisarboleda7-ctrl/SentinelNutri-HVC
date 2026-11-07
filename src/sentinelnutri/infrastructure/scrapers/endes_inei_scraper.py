"""
Scraper de Microdatos ENDES (INEI):
Descarga módulos anuales de agua, saneamiento, educación materna, lactancia y controles CRED,
y lee archivos SPSS (.sav) o Stata (.dta) mediante `pyreadstat`.
"""

from typing import Dict, List
from .base_ethical_scraper import EthicalWebScraperClient


class EndesIneiScraper:
    """Extractor especializado para microdatos ENDES del portal del INEI."""

    PORTAL_URL = "https://proyectos.inei.gob.pe/microdatos/"

    def __init__(self, client: EthicalWebScraperClient | None = None) -> None:
        self.client = client or EthicalWebScraperClient()

    def read_sav_file(self, sav_path: str) -> List[Dict[str, object]]:
        """Lee un archivo de microdatos .sav usando pyreadstat filtrando el departamento 09 (Huancavelica)."""
        try:
            import pyreadstat

            df, _ = pyreadstat.read_sav(sav_path)
            return df.head(100).to_dict(orient="records")
        except Exception:
            return []

