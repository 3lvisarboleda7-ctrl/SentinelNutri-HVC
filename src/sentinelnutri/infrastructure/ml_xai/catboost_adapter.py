"""
Adaptador de Carga de Artefactos CatBoost (.cbm) desde el HDD de 1 TB del Equipo 2.
"""

import os
from typing import Any, Optional


class CatBoostModelLoader:
    """Gestiona la carga en memoria del modelo `.cbm` entrenado en Google Colab."""

    def __init__(self, models_dir: Optional[str] = None) -> None:
        self.models_dir = models_dir or os.getenv("MODELS_DIR", "./data/models")
        self.model_path = os.path.join(self.models_dir, "catboost_dci_hvc.cbm")

    def load_native_catboost_if_available(self) -> Optional[Any]:
        """Carga el binario `.cbm` con la librería `catboost` si se encuentra disponible en el contenedor."""
        if not os.path.exists(self.model_path):
            return None
        try:
            from catboost import CatBoostClassifier

            model = CatBoostClassifier()
            model.load_model(self.model_path)
            return model
        except Exception:
            return None

