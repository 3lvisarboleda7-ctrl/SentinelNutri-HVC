"""Vista 2 del Dashboard Streamlit: Soporte a Auditoría S3* (Explicabilidad XAI - SHAP)."""

import streamlit as st
from sentinelnutri.interfaces.dashboard.app import init_services

st.set_page_config(page_title="Auditoría S3* SHAP | SentinelNutri-HVC", layout="wide")
repo, _, _, _, tool4, _, _ = init_services()

st.header("Soporte a S3* (Auditoría): Explicaciones SHAP Locales por Distrito")
preds = repo.get_latest_predictions()
options = {f"{p.ubigeo} - {p.distrito} ({p.provincia})": p.ubigeo for p in preds}
choice = st.selectbox("Distrito a auditar:", list(options.keys()))
exp = tool4.execute(options[choice])
st.table(exp["contribuciones_shap_ordenadas"])

