"""Vista 2 del Dashboard Streamlit: Soporte a Auditoría S3* (Explicabilidad XAI - SHAP)."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from sentinelnutri.interfaces.dashboard.app import init_services

st.set_page_config(page_title="Auditoría S3* SHAP | SentinelNutri-HVC", page_icon="🔍", layout="wide")
repo, predictor, _, _, tool4, _, _ = init_services()

st.header("🔍 Soporte a S3* (Auditoría): Explicabilidad XAI mediante Valores SHAP")
st.caption("Descomposición local por distrito y ranking global de determinantes estructurales de la DCI en Huancavelica.")

preds = repo.get_latest_predictions()
options = {f"{p.ubigeo} - {p.distrito} ({p.provincia})": p.ubigeo for p in preds}
choice = st.selectbox("Distrito a auditar:", list(options.keys()))
exp = tool4.execute(options[choice])

col_local, col_global = st.columns(2)

with col_local:
    shap_items = exp.get("contribuciones_shap_ordenadas", [])
    if shap_items:
        df_shap = pd.DataFrame(shap_items[:8]).iloc[::-1]
        fig_local, ax_local = plt.subplots(figsize=(6.8, 4.3), dpi=130)
        colors = ["#e74c3c" if v > 0 else "#27ae60" for v in df_shap["aporte_shap_puntos_pct"]]
        bars = ax_local.barh(df_shap["determinante"], df_shap["aporte_shap_puntos_pct"], color=colors, height=0.62)
        ax_local.axvline(0.0, color="#333333", linewidth=1.1)
        for bar, val in zip(bars, df_shap["aporte_shap_puntos_pct"]):
            ha = "left" if val >= 0 else "right"
            offset = 0.04 if val >= 0 else -0.04
            ax_local.text(val + offset, bar.get_y() + bar.get_height() / 2, f"{val:+.2f}", va="center", ha=ha, fontsize=8)
        ax_local.set_title(
            f"SHAP Local: {exp['distrito']} (DCI Proyectada: {exp['dci_proyectada_pct']}%)",
            fontsize=9.5,
            fontweight="bold",
        )
        ax_local.set_xlabel("Impacto SHAP (puntos porcentuales)", fontsize=8.5)
        ax_local.grid(axis="x", linestyle="--", alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig_local)
        plt.close(fig_local)

with col_global:
    metrics = predictor.train_and_evaluate(repo.get_historical_series(anio_inicio=2014, anio_fin=2024))
    global_shap = sorted(metrics["importancia_global_shap"], key=lambda x: x["mean_abs_shap"])
    fig_glob, ax_glob = plt.subplots(figsize=(6.8, 4.3), dpi=130)
    labels = [g["etiqueta"] for g in global_shap]
    vals = [g["mean_abs_shap"] for g in global_shap]
    bars_g = ax_glob.barh(labels, vals, color="#1b6ca8", height=0.65)
    for bar, val in zip(bars_g, vals):
        ax_glob.text(val + 0.03, bar.get_y() + bar.get_height() / 2, f"{val:.2f}", va="center", fontsize=8)
    ax_glob.set_xlim(0, max(vals) * 1.18 if vals else 1.0)
    ax_glob.set_title("Importancia Global |SHAP| (100 Distritos, 2014–2024)", fontsize=9.5, fontweight="bold")
    ax_glob.set_xlabel("Impacto Medio Absoluto (puntos %)", fontsize=8.5)
    ax_glob.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig_glob)
    plt.close(fig_glob)

st.subheader("Detalle Tabular de Contribuciones SHAP")
st.dataframe(pd.DataFrame(exp["contribuciones_shap_ordenadas"]), use_container_width=True)
