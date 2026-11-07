"""Router de diagnóstico de infraestructura (PostgreSQL, HDD 1TB, Ollama GTX 1050 y Reglas Fijas)."""

import os
from typing import Dict
from fastapi import APIRouter
from sentinelnutri.config import detect_current_node

router = APIRouter(tags=["Infraestructura"])


@router.get("/infrastructure/status")
def get_infrastructure_status() -> Dict[str, object]:
    node = detect_current_node()
    return {
        "detected_node": node.to_dict(),
        "node_role": os.getenv("NODE_ROLE", node.node_id),
        "raw_data_dir": node.active_raw_data_dir,
        "models_dir": node.active_models_dir,
        "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "algedonic_threshold_pct": float(os.getenv("ALGEDONIC_DCI_THRESHOLD", "25.0")),
        "require_human_approval_s3": True,
    }
