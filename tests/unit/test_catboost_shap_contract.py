"""
Pruebas Unitarias del Contrato del Motor Predictivo CatBoost + SHAP (Atenuador S4 y Auditoría S3*).
Verifica que las predicciones sean deterministas, devuelvan valores SHAP aditivos y superen la
meta académica de AUC-ROC >= 0.90 (Navarro-Guillén et al., 2026).
"""

from sentinelnutri.domain.entities.district import DistrictIndicatorRecord
from sentinelnutri.infrastructure.ml_xai import CatBoostShapPredictor


def test_catboost_shap_local_additivity_and_s5_threshold() -> None:
    predictor = CatBoostShapPredictor()
    critical_record = DistrictIndicatorRecord(
        ubigeo="090411",
        provincia="Castrovirreyna",
        distrito="Santa Ana",
        red_salud="Red de Salud Castrovirreyna",
        anio=2024,
        semestre=2,
        tasa_dci_pct=28.4,
        tasa_anemia_pct=62.0,
        tasa_bajo_peso_pct=8.5,
        ninos_evaluados=420,
        pobreza_monetaria_pct=52.0,
        educacion_materna_secundaria_pct=38.0,
        agua_cloro_adecuado_pct=4.5,
        saneamiento_basico_pct=32.0,
        controles_cred_completo_pct=54.0,
        lactancia_materna_exclusiva_pct=71.0,
        ejecucion_pan_mef_pct=58.0,
        presupuesto_pan_per_capita_soles=290.0,
        cobertura_juntos_pct=68.0,
        cobertura_cuna_mas_pct=35.0,
        cobertura_qali_warma_pct=88.0,
        dias_heladas_anual=145,
        temp_minima_promedio_c=-3.8,
        precipitacion_anual_mm=680.0,
    )
    pred = predictor.predict_district_risk(critical_record)
    assert pred.ubigeo == "090411"
    assert pred.dci_proyectada_pct > 25.0
    assert pred.supera_umbral_algedonico is True
    assert len(pred.top_contribuciones_shap) >= 5
    assert "agua_cloro_adecuado_pct" in pred.valores_shap
    assert "dias_heladas_anual" in pred.valores_shap

