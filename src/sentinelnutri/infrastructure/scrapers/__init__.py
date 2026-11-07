"""Subsistema de Extracción Automatizada y Ética (Tabla 4 del Perfil de Proyecto)."""

from .base_ethical_scraper import EthicalWebScraperClient
from .multi_source_orchestrator import MultiSourceScraperOrchestrator

__all__ = ["EthicalWebScraperClient", "MultiSourceScraperOrchestrator"]

