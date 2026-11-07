"""Router de Metadatos del Motor Predictivo CatBoost + SHAP."""

from typing import Dict
from fastapi import APIRouter
from sentinelnutri.infrastructure.ml_xai.catboost_shap_predictor import FEATURE_METADATA

router = APIRouter(tags=["Motor Predictivo CatBoost + SHAP y Herramienta 3"])


@router.get("/predict/features")
def get_model_features_metadata() -> Dict[str, object]:
    return {
        "modelo": "CatBoost + SHAP (TreeExplainer)",
        "umbral_algedonico_fijo_pct": 25.0,
        "variables_predictoras": [
            {
                "variable": var,
                "etiqueta": label,
                "media_referencia_regional": ref_mean,
                "peso_estructural": weight,
            }
            for var, label, ref_mean, weight in FEATURE_METADATA
        ],
    }

