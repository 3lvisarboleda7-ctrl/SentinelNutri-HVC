"""
Pipeline de Ingeniería de Características para las 5 Dimensiones Determinantes de la DCI en los Andes
(Castro-Bedriñana et al., 2021; Navarro-Guillén et al., 2026).

Calcula indicadores compuestos para alimentar el motor CatBoost + SHAP:
- Brecha de calidad de agua segura (100 - agua_cloro_adecuado_pct).
- Índice de severidad agroclimática por heladas en altitud (> 3 500 m s. n. m.).
- Eficiencia de absorción presupuestal del Programa Articulado Nutricional (PAN 0001 - MEF).
- Índice de protección articulada MIDIS (Juntos + Cuna Más + Qali Warma).
"""

from typing import Dict
from sentinelnutri.domain.entities.district import DistrictIndicatorRecord


def compute_derived_andino_features(record: DistrictIndicatorRecord) -> Dict[str, float]:
    """Transforma un registro distrital en el vector enriquecido de características del modelo."""
    brecha_cloro_pct = max(0.0, 100.0 - record.agua_cloro_adecuado_pct)
    altitud = float(record.altitud_msnm or 3400)
    severidad_heladas = (record.dias_heladas_anual / 120.0) * (altitud / 3500.0)
    indice_midis = (
        0.40 * record.cobertura_cuna_mas_pct
        + 0.35 * record.cobertura_juntos_pct
        + 0.25 * record.cobertura_qali_warma_pct
    )
    eficiencia_pan = (record.ejecucion_pan_mef_pct / 100.0) * (record.presupuesto_pan_per_capita_soles / 400.0)

    return {
        "tasa_dci_pct": float(record.tasa_dci_pct),
        "agua_cloro_adecuado_pct": float(record.agua_cloro_adecuado_pct),
        "dias_heladas_anual": float(record.dias_heladas_anual),
        "pobreza_monetaria_pct": float(record.pobreza_monetaria_pct),
        "ejecucion_pan_mef_pct": float(record.ejecucion_pan_mef_pct),
        "controles_cred_completo_pct": float(record.controles_cred_completo_pct),
        "tasa_anemia_pct": float(record.tasa_anemia_pct),
        "educacion_materna_secundaria_pct": float(record.educacion_materna_secundaria_pct),
        "cobertura_juntos_pct": float(record.cobertura_juntos_pct),
        "cobertura_cuna_mas_pct": float(record.cobertura_cuna_mas_pct),
        "brecha_cloro_pct": round(brecha_cloro_pct, 2),
        "severidad_heladas_idx": round(severidad_heladas, 4),
        "indice_articulacion_midis": round(indice_midis, 2),
        "eficiencia_presupuestal_pan": round(eficiencia_pan, 4),
    }

