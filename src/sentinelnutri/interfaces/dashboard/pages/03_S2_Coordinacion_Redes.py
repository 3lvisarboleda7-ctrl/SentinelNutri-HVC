"""Vista 3 del Dashboard Streamlit: Coordinación S2 de las 7 Redes de Salud Provinciales."""

import streamlit as st
from sentinelnutri.interfaces.dashboard.app import init_services

st.set_page_config(page_title="Coordinación S2 | SentinelNutri-HVC", layout="wide")
repo, _, _, _, _, _, _ = init_services()

st.header("Soporte a S2 (Coordinación): Las 7 Redes de Salud Provinciales y OEI del PEI 2020-2027")
alerts = repo.get_all_alerts()
if not alerts:
    st.info("No existen alertas registradas aún en la bandeja de coordinación S2/S3.")
else:
    st.dataframe(alerts, use_container_width=True)


