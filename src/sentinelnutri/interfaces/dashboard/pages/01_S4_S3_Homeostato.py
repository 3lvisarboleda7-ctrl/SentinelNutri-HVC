"""Vista 1 del Dashboard Streamlit: Homeostato S3-S4 (Control vs. Inteligencia)."""

import streamlit as st
from sentinelnutri.interfaces.dashboard.app import init_services

st.set_page_config(page_title="Homeostato S3-S4 | SentinelNutri-HVC", layout="wide")
repo, _, _, tool3, _, _, _ = init_services()

st.header("Homeostato S3–S4: Estado Actual de la Operación (S3) vs. Proyecciones del Sistema 4")
preds = repo.get_latest_predictions()
if not preds:
    tool3.execute(anio_corte=2024)
    preds = repo.get_latest_predictions()

st.dataframe(
    [
        {
            "Ubigeo": p.ubigeo,
            "Provincia": p.provincia,
            "Distrito": p.distrito,
            "DCI Actual S3 (%)": p.dci_actual_pct,
            "DCI Proyectada S4 (%)": p.dci_proyectada_pct,
            "Nivel de Riesgo": p.nivel_riesgo.value,
            "Supera Umbral Algedónico (25%)": p.supera_umbral_algedonico,
        }
        for p in preds
    ],
    use_container_width=True,
)

