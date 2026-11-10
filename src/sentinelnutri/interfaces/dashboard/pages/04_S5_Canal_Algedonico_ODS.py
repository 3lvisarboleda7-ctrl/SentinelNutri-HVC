"""Vista 4 del Dashboard Streamlit: Canal Algedónico S5, Registro de Cargas y ODS 2, 3 y 6."""

import streamlit as st
from sentinelnutri.interfaces.dashboard.app import get_cached_evaluation_metrics, init_services

st.set_page_config(page_title="Canal Algedónico S5 y Gobernanza | SentinelNutri-HVC", layout="wide")
repo, predictor, _, _, _, _, _ = init_services()

st.header("Canal Algedónico Automatizado (S1/S4 -> S5) y Marco de Gobernanza (ODS 2, 3 y 6)")
metrics = get_cached_evaluation_metrics(repo, predictor)
st.json(metrics["metricas_globales"])
st.subheader("Registro de Cargas (Control de Fecha + Huella Digital SHA-256)")
st.dataframe(repo.get_recent_loads(limit=20), use_container_width=True)


