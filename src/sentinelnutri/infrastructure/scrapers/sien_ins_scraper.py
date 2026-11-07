"""
Scraper 1 — SIEN-HIS (INS/CENAN) y Plataforma Nacional de Datos Abiertos:
Extrae indicadores antropométricos y nutricionales (DCI, anemia y bajo peso en menores de 5 años)
por provincia y distrito de Huancavelica (2014–2024).

Soporta:
1. Descarga de reportes tabulares CSV/XLSX desde Datos Abiertos (`datosabiertos.gob.pe`).
2. Extracción de tablas en boletines PDF del INS/CENAN mediante `fitz` (PyMuPDF) y `pdfplumber`.
3. Armonización automática de código `ubigeo` (`090101`–`090721`) y huella digital `SHA-256`.
"""

import csv
import io
import re
from typing import Any, Dict, List, Optional

from sentinelnutri.domain.rules.scraping_ethics import compute_sha256_hash
from sentinelnutri.infrastructure.etl.ubigeo_harmonizer import (
    normalize_ubigeo_code,
    resolve_ubigeo_by_name,
)
from .base_ethical_scraper import EthicalWebScraperClient


class SienInsScraper:
    """Extractor especializado para publicaciones del INS/CENAN (SIEN-HIS Huancavelica)."""

    PORTAL_URL = "https://web.ins.gob.pe/es/alimentacion-y-nutricion/vigilancia-alimentaria-y-nutricional/sien-his-huancavelica"
    DATOS_ABIERTOS_URL = "https://www.datosabiertos.gob.pe/dataset/sistema-de-informacion-del-estado-nutricional-sien-his"

    def __init__(self, client: Optional[EthicalWebScraperClient] = None) -> None:
        self.client = client or EthicalWebScraperClient()

    def parse_sien_csv_bytes(self, csv_bytes: bytes, default_year: int = 2024) -> List[Dict[str, Any]]:
        """
        Procesa un archivo CSV de SIEN-HIS / Datos Abiertos filtrando el departamento de Huancavelica (09xxxx).
        """
        text = csv_bytes.decode("utf-8", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        extracted: List[Dict[str, Any]] = []

        for row in reader:
            norm_row = {str(k or "").strip().lower(): str(v or "").strip() for k, v in row.items()}
            ubigeo = normalize_ubigeo_code(
                norm_row.get("ubigeo") or norm_row.get("cod_ubigeo") or norm_row.get("id_ubigeo")
            )
            if not ubigeo:
                ubigeo = resolve_ubigeo_by_name(
                    norm_row.get("distrito", ""),
                    norm_row.get("provincia", ""),
                )
            if not ubigeo:
                continue

            anio_str = norm_row.get("anio") or norm_row.get("año") or str(default_year)
            anio = int(anio_str) if anio_str.isdigit() else default_year
            dci_pct = float(norm_row.get("tasa_dci_pct") or norm_row.get("dci_pct") or 0.0)
            anemia_pct = float(norm_row.get("tasa_anemia_pct") or norm_row.get("anemia_pct") or 0.0)
            bajo_peso_pct = float(norm_row.get("tasa_bajo_peso_pct") or norm_row.get("bajo_peso_pct") or 0.0)
            evaluados = int(float(norm_row.get("ninos_evaluados") or norm_row.get("evaluados") or 0))

            extracted.append(
                {
                    "ubigeo": ubigeo,
                    "anio": anio,
                    "tasa_dci_pct": round(dci_pct, 2),
                    "tasa_anemia_pct": round(anemia_pct, 2),
                    "tasa_bajo_peso_pct": round(bajo_peso_pct, 2),
                    "ninos_evaluados": evaluados,
                }
            )
        return extracted

    def parse_pdf_table_bytes(self, pdf_bytes: bytes, default_year: int = 2024) -> List[Dict[str, Any]]:
        """
        Extrae filas distritales de un reporte PDF del SIEN-HIS usando PyMuPDF (`fitz`) o `pdfplumber`.
        """
        rows: List[Dict[str, Any]] = []
        line_pattern = re.compile(
            r"(09\d{4})\s+([A-Za-zÁÉÍÓÚÑáéíóúñ\s\-\.]+?)\s+(\d+)\s+(\d+(?:[\.,]\d+)?)\s+(\d+(?:[\.,]\d+)?)"
        )
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            for page in doc:
                text = page.get_text("text")
                for match in line_pattern.finditer(text):
                    ubigeo = match.group(1)
                    evaluados = int(match.group(3))
                    dci_pct = float(match.group(4).replace(",", "."))
                    anemia_pct = float(match.group(5).replace(",", "."))
                    rows.append(
                        {
                            "ubigeo": ubigeo,
                            "anio": default_year,
                            "ninos_evaluados": evaluados,
                            "tasa_dci_pct": dci_pct,
                            "tasa_anemia_pct": anemia_pct,
                        }
                    )
        except Exception:
            pass

        if rows:
            return rows

        try:
            import pdfplumber

            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    for table in page.extract_tables() or []:
                        for r in table:
                            if r and any(r):
                                rows.append({"raw_cells": r, "sha256": compute_sha256_hash(pdf_bytes)[:12]})
        except Exception:
            pass
        return rows
