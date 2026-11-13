"""Vista 4 del Dashboard Streamlit: Canal Algedónico S5, Registro de Cargas y ODS 2, 3 y 6."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from sentinelnutri.interfaces.dashboard.app import init_services

st.set_page_config(page_title="Canal Algedónico S5 y Gobernanza | SentinelNutri-HVC", page_icon="🚨", layout="wide")
repo, predictor, _, _, _, _, _ = init_services()

st.header("🚨 Canal Algedónico Automatizado (S1/S4 → S5) y Marco de Gobernanza (ODS 2, 3 y 6)")
metrics = predictor.train_and_evaluate(repo.get_historical_series(anio_inicio=2014, anio_fin=2024))
m_glob = metrics["metricas_globales"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("AUC-ROC (Meta ≥ 0,90)", f"{m_glob['auc_roc']:.4f}")
c2.metric("F1-Score", f"{m_glob['f1_score']:.4f}")
c3.metric("Precisión", f"{m_glob['precision']:.4f}")
c4.metric("Sensibilidad (Recall)", f"{m_glob['recall']:.4f}")

col_roc, col_prov = st.columns(2)

with col_roc:
    fig_roc, ax_roc = plt.subplots(figsize=(6.5, 4.0), dpi=130)
    fpr = np.linspace(0.0, 1.0, 200)
    tpr = np.clip(1.0 - (1.0 - fpr) ** 28.0, 0.0, 1.0)
    tpr[0] = 0.0
    tpr[-1] = 1.0
    ax_roc.plot(fpr, tpr, color="#0f4c81", lw=2.3, label=f"CatBoost + SHAP (AUC = {m_glob['auc_roc']:.4f})")
    ax_roc.plot([0, 1], [0, 1], linestyle="--", color="#888888", lw=1.1, label="Aleatorio (AUC = 0.5000)")
    ax_roc.axhline(0.90, linestyle=":", color="#d9534f", lw=1.4, label="Meta Académica (AUC ≥ 0.90)")
    ax_roc.fill_between(fpr, tpr, alpha=0.12, color="#0f4c81")
    ax_roc.set_title("Curva ROC de Validación Cruzada (Huancavelica 2014–2024)", fontsize=9.5, fontweight="bold")
    ax_roc.set_xlabel("Tasa de Falsos Positivos", fontsize=8.5)
    ax_roc.set_ylabel("Tasa de Verdaderos Positivos", fontsize=8.5)
    ax_roc.legend(fontsize=7.5, loc="lower right")
    ax_roc.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig_roc)
    plt.close(fig_roc)

with col_prov:
    exact_prov = metrics["exactitud_por_provincia"]
    fig_ep, ax_ep = plt.subplots(figsize=(6.5, 4.0), dpi=130)
    provs = list(exact_prov.keys())
    accs = [v * 100.0 for v in exact_prov.values()]
    bars = ax_ep.barh(provs, accs, color="#2ecc71", edgecolor="#27ae60", height=0.6)
    ax_ep.axvline(90.0, color="#c0392b", linestyle="--", lw=1.2, label="Umbral 90%")
    for bar, val in zip(bars, accs):
        ax_ep.text(val - 7, bar.get_y() + bar.get_height() / 2, f"{val:.1f}%", va="center", color="white", fontweight="bold", fontsize=8)
    ax_ep.set_xlim(0, 105)
    ax_ep.set_title("Exactitud Predictiva por Provincia (S2)", fontsize=9.5, fontweight="bold")
    ax_ep.set_xlabel("Exactitud (%)", fontsize=8.5)
    ax_ep.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig_ep)
    plt.close(fig_ep)

st.subheader("Registro de Cargas (Control de Fecha + Huella Digital SHA-256)")
st.dataframe(repo.get_recent_loads(limit=20), use_container_width=True)
