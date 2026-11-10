"""
Dashboard Cibernético de Alertas Priorizadas — SentinelNutri-HVC (Streamlit).

Materializa en una sola interfaz los canales del Modelo de Sistema Viable del GORE Huancavelica:
1. Homeostato S3-S4: Estado actual de la operación (S3 - GRDS) vs. proyecciones del S4 (CatBoost),
   mapas de calor distritales y paradoja presupuesto MEF vs. brecha de DCI.
2. Auditoría S3* (Explicabilidad XAI - SHAP): Valores SHAP locales por distrito y ranking global.
3. Coordinación S2 (Redes de Salud Provinciales): Indicadores compartidos para las 7 provincias
   y recomendaciones diferenciadas por sector (Salud, Agua, Agricultura) alineadas a los OEI del PEI 2020-2027.
4. Canal Algedónico S5 y Gobernanza: Señales algedónicas directas al Consejo Regional (DCI > 25%),
   bandeja de aprobación humana (HITL), registro de cargas (fecha + hash SHA-256) y alineación con ODS 2, 3 y 6.
"""

import os
from typing import Any, Dict, Optional

try:
    import streamlit as st
except ImportError:  # Permite importar los helpers de estado del Dashboard en runners CI ligeros sin UI
    st = None  # type: ignore[assignment]

from sentinelnutri.application import (
    Tool1ExtraerFuentesUseCase,
    Tool3PredecirRiesgoUseCase,
    Tool4ExplicarRiesgoUseCase,
    Tool5RedactarInformeUseCase,
    Tool6NotificarUseCase,
)
from sentinelnutri.infrastructure.ml_xai import CatBoostShapPredictor
from sentinelnutri.infrastructure.persistence import (
    SqlAlchemyRepository,
    create_db_engine_and_session,
)
from sentinelnutri.infrastructure.scrapers import MultiSourceScraperOrchestrator

_EVAL_METRICS_CACHE: Dict[str, Dict[str, Any]] = {}


def init_services(database_url: Optional[str] = None):
    """Inicializa los servicios del Dashboard garantizando serie histórica y predicciones no vacías."""
    db_file, session_factory = create_db_engine_and_session(database_url)
    repo = SqlAlchemyRepository(session_factory)
    scraper = MultiSourceScraperOrchestrator(repository=repo)
    predictor = CatBoostShapPredictor()

    tool1 = Tool1ExtraerFuentesUseCase(repo, scraper)
    tool3 = Tool3PredecirRiesgoUseCase(repo, predictor)
    tool4 = Tool4ExplicarRiesgoUseCase(repo, predictor)
    tool5 = Tool5RedactarInformeUseCase()
    tool6 = Tool6NotificarUseCase(repo)

    if not repo.get_historical_series(anio_inicio=2014, anio_fin=2024):
        tool1.execute(mode="backfill", start_year=2014, end_year=2024, force_rebuild=True)
    if not repo.get_latest_predictions():
        tool3.execute(anio_corte=2024)

    return repo, predictor, tool1, tool3, tool4, tool5, tool6


def get_cached_evaluation_metrics(
    repo: SqlAlchemyRepository,
    predictor: CatBoostShapPredictor,
    cache_key: str = "default",
) -> Dict[str, Any]:
    """Obtiene y almacena en caché las métricas de validación cruzada para evitar recálculo en cada render."""
    if cache_key not in _EVAL_METRICS_CACHE:
        series = repo.get_historical_series(anio_inicio=2014, anio_fin=2024)
        _EVAL_METRICS_CACHE[cache_key] = predictor.train_and_evaluate(series)
    return _EVAL_METRICS_CACHE[cache_key]


def build_dashboard_rooms_snapshot(database_url: Optional[str] = None) -> Dict[str, Any]:
    """Construye de forma determinista el estado de las 4 salas MSV para pruebas e inspección rápida."""
    key = database_url or os.getenv("DATABASE_URL", "default")
    repo, predictor, _, tool3, tool4, _, _ = init_services(database_url)
    preds = repo.get_latest_predictions()
    if not preds:
        tool3.execute(anio_corte=2024)
        preds = repo.get_latest_predictions()

    options = {f"{p.ubigeo} - {p.distrito} ({p.provincia})": p.ubigeo for p in preds}
    first_ubigeo = next(iter(options.values())) if options else "090101"
    shap_audit = tool4.execute(first_ubigeo)
    alerts = repo.get_all_alerts()
    metrics = get_cached_evaluation_metrics(repo, predictor, cache_key=key)

    return {
        "sala_1_homeostato_count": len(preds),
        "sala_1_criticos_s5_count": sum(1 for p in preds if p.supera_umbral_algedonico),
        "sala_2_shap_options_count": len(options),
        "sala_2_sample_explanation": shap_audit,
        "sala_3_alerts_count": len(alerts),
        "sala_4_metrics_globales": metrics["metricas_globales"],
        "sala_4_loads_count": len(repo.get_recent_loads(limit=20)),
    }


def main() -> None:
    st.set_page_config(
        page_title="SentinelNutri-HVC | Sistema 4 MSV - GORE Huancavelica",
        layout="wide",
    )
    repo, predictor, tool1, tool3, tool4, tool5, tool6 = init_services()

    st.title("SentinelNutri-HVC: Sistema Inteligente de Alerta Temprana para el Sistema 4 del MSV")
    st.caption(
        "Gobierno Regional de Huancavelica (GORE-HVC) · Arquitectura de Costo Cero · "
        "CatBoost + SHAP (XAI) + Agente Supervisor n8n + Reglas Fijas Cibernéticas"
    )

    preds = repo.get_latest_predictions()
    if not preds:
        tool3.execute(anio_corte=2024)
        preds = repo.get_latest_predictions()

    criticos = [p for p in preds if p.supera_umbral_algedonico]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Distritos Monitoreados (7 Provincias)", len(preds))
    col2.metric(
        "Promedio DCI Proyectada (S4)",
        f"{sum(p.dci_proyectada_pct for p in preds) / max(1, len(preds)):.1f} %",
        delta="Brecha vs. 12,1 % nacional",
        delta_color="inverse",
    )
    col3.metric("Alertas Algedónicas S5 (DCI > 25 %)", len(criticos))
    col4.metric("Umbral Algedónico Fijo (Nodo IF)", "25,0 %")

    tab_s3_s4, tab_s3_star, tab_s2, tab_s5 = st.tabs(
        [
            "1. Homeostato S3–S4 (Control vs. Inteligencia)",
            "2. Auditoría S3* (Explicaciones SHAP)",
            "3. Coordinación S2 (7 Redes de Salud y PEI 2020-2027)",
            "4. Canal Algedónico S5, HITL y Gobernanza (ODS 2, 3, 6)",
        ]
    )

    with tab_s3_s4:
        st.subheader("Homeostato S3–S4: Estado Actual de la Operación vs. Proyección del Sistema 4")
        st.dataframe(
            [
                {
                    "Ubigeo": p.ubigeo,
                    "Provincia": p.provincia,
                    "Distrito": p.distrito,
                    "Red de Salud (S2)": p.red_salud,
                    "DCI Actual S3 (%)": p.dci_actual_pct,
                    "DCI Proyectada S4 (%)": p.dci_proyectada_pct,
                    "Prob. Riesgo Crítico": p.probabilidad_riesgo_critico,
                    "Nivel de Riesgo": p.nivel_riesgo.value,
                    "Canal Algedónico S5 (>25%)": "SÍ (CRÍTICO)" if p.supera_umbral_algedonico else "No (Canal S3)",
                }
                for p in preds
            ],
            use_container_width=True,
        )

    with tab_s3_star:
        st.subheader("Soporte a S3* (Auditoría mediante Explicabilidad XAI - Valores SHAP por Distrito)")
        options = {f"{p.ubigeo} - {p.distrito} ({p.provincia})": p.ubigeo for p in preds}
        selected_label = st.selectbox("Seleccione un distrito para auditar su clasificación:", list(options.keys()))
        selected_ubigeo = options.get(selected_label) or next(iter(options.values()), "090101")
        explanation = tool4.execute(selected_ubigeo)

        st.markdown(
            f"**Distrito:** `{explanation['distrito']}` ({explanation['provincia']}) | "
            f"**DCI Actual:** `{explanation['dci_actual_pct']} %` | "
            f"**DCI Proyectada (CatBoost):** `{explanation['dci_proyectada_pct']} %` | "
            f"**Nivel de Riesgo:** `{explanation['nivel_riesgo']}`"
        )
        st.table(explanation["contribuciones_shap_ordenadas"])

    with tab_s2:
        st.subheader("Soporte a S2 (Coordinación de las 7 Redes de Salud Provinciales y Recomendaciones OEI PEI 2020-2027)")
        if st.button("Generar Recomendación Sectorial para el Distrito Seleccionado"):
            exp = tool4.execute(selected_ubigeo)
            rep = tool5.execute(exp)
            tool6.execute_dispatch(rep["informe"])
            st.success("Informe generado y enrutado según las Reglas Fijas del MSV.")

        alerts = repo.get_all_alerts()
        if not alerts:
            st.info("No existen alertas generadas aún en la bandeja S2/S3.")
        for a in alerts[:10]:
            with st.expander(
                f"[{a['canal_destino']} | {a['estado_aprobacion_humana']}] "
                f"{a['distrito']} ({a['provincia']}) - {a['fecha_creacion']}"
            ):
                st.write("**Síntesis Narrativa S4:**", a["sintesis_narrativa_s4"])
                st.write("- **Salud (DIRESA):**", a["recomendacion_salud"])
                st.write("- **Agua y Saneamiento (DRVCS):**", a["recomendacion_agua_saneamiento"])
                st.write("- **Agricultura, MEF y MIDIS:**", a["recomendacion_agricultura_midis"])
                st.caption(f"Alineación: {a['oei_pei_vinculados']} | {a['ods_vinculados']}")

    with tab_s5:
        st.subheader("Canal Algedónico Automatizado (S1/S4 -> S5) y Marco de Gobernanza")
        metrics = get_cached_evaluation_metrics(repo, predictor)
        m_glob = metrics["metricas_globales"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("AUC-ROC (Meta >= 0.90)", m_glob["auc_roc"])
        c2.metric("F1-Score", m_glob["f1_score"])
        c3.metric("Precisión", m_glob["precision"])
        c4.metric("Recall", m_glob["recall"])

        st.markdown("#### Registro de Cargas y Huella Digital SHA-256 (PostgreSQL)")
        st.dataframe(repo.get_recent_loads(limit=15), use_container_width=True)


if __name__ == "__main__":
    main()

