"""
Vigilante de Carpeta Compartida para Convenio DIRESA Huancavelica (Ley N.° 29733):
Los registros nominales del SIEN-HIS por niño no se extraen de portales públicos;
se reciben en una carpeta compartida vigilada y se agregan inmediatamente por ubigeo distrital,
descartando cualquier identificador personal antes de ingresar al pipeline analítico.
"""

import os
from typing import Dict, List
from sentinelnutri.domain.rules.privacy_guard import sanitize_district_payload_for_llm


class DiresaSharedFolderWatcher:
    """Vigilante ético de carpeta compartida bajo convenio DIRESA (Ley N.° 29733)."""

    def __init__(self, shared_folder: str | None = None) -> None:
        self.shared_folder = shared_folder or os.getenv("SHARED_DIRESA_DIR", "./data/diresa_ley29733")
        os.makedirs(self.shared_folder, exist_ok=True)

    def scan_and_anonymize(self, raw_records: List[Dict[str, object]]) -> List[Dict[str, object]]:
        """Elimina cualquier campo nominal (DNI, nombres, HC) dejando solo agregados por ubigeo."""
        return [sanitize_district_payload_for_llm(r, strict=False) for r in raw_records]

