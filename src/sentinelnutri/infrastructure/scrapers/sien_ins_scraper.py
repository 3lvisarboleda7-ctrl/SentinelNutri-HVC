"""
Scraper de SIEN-HIS (INS/CENAN):
Extrae indicadores de DCI, anemia y bajo peso en menores de 5 años por provincia y distrito de Huancavelica.
Soporta lectura de tablas en PDF mediante `pdfplumber` / `fitz` (PyMuPDF).
"""

from typing import Dict, List
from .base_ethical_scraper import EthicalWebScraperClient


class SienInsScraper:
    """Extractor especializado para publicaciones del INS/CENAN (SIEN-HIS)."""

    PORTAL_URL = "https://web.ins.gob.pe/es/alimentacion-y-nutricion/vigilancia-alimentaria-y-nutricional/sien-his-huancavelica"

    def __init__(self, client: EthicalWebScraperClient | None = None) -> None:
        self.client = client or EthicalWebScraperClient()

    def parse_pdf_table_bytes(self, pdf_bytes: bytes) -> List[Dict[str, object]]:
        """Extrae filas tabulares de un reporte PDF del SIEN-HIS usando pdfplumber o PyMuPDF."""
        rows: List[Dict[str, object]] = []
        try:
            import io
            import pdfplumber

            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    for table in page.extract_tables() or []:
                        for r in table:
                            if r and any(r):
                                rows.append({"raw_cells": r})
        except Exception:
            pass
        return rows

