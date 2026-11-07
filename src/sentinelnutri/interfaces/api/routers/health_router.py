"""Router de diagnóstico de infraestructura (PostgreSQL, HDD 1TB, Ollama GTX 1050 y Reglas Fijas)."""

import os
from typing import Dict
from fastapi import APIRouter

router = APIRouter(tags=["Infraestructura"])


@router.get("/infrastructure/status")
def get_infrastructure_status() -> Dict[str, object]:
    return {
        "node_role": os.getenv("NODE_ROLE", "EQUIPO_1_DEV_WORKSTATION"),
        "raw_data_dir": os.getenv("RAW_DATA_DIR", "./data/raw"),
        "models_dir": os.getenv("MODELS_DIR", "./data/models"),
        "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "algedonic_threshold_pct": float(os.getenv("ALGEDONIC_DCI_THRESHOLD", "25.0")),
        "require_human_approval_s3": True,
    }

