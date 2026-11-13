"""Vista 1 del Dashboard Streamlit: Homeostato S3-S4 (Control vs. Inteligencia)."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from sentinelnutri.interfaces.dashboard.app import init_services

st.set_page_config(page_title="Homeostato S3-S4 | SentinelNutri-HVC", page_icon="📊", layout="wide")
repo, _, _, tool3, _, _, _ = init_services()

st.header("📊 Homeostato S3–S4: Estado Actual (S3) vs. Proyecciones del Sistema 4")
st.caption("Comparativa territorial de los 100 distritos de las 7 provincias de Huancavelica y umbral algedónico (25,0 %).")

preds = repo.get_latest_predictions()
if not preds:
    tool3.execute(anio_corte=2024)
    preds = repo.get_latest_predictions()

districts_meta = {d.ubigeo: d for d in repo.get_all_districts()}

df_preds = pd.DataFrame(
    [
        {
            "ubigeo": p.ubigeo,
            "provincia": p.provincia,
            "distrito": p.distrito,
            "red_salud": p.red_salud,
            "dci_actual": p.dci_actual_pct,
            "dci_proyectada": p.dci_proyectada_pct,
            "riesgo": p.nivel_riesgo.value,
            "algedonico": p.supera_umbral_algedonico,
            "lat": districts_meta[p.ubigeo].latitud if p.ubigeo in districts_meta else -12.78,
            "lon": districts_meta[p.ubigeo].longitud if p.ubigeo in districts_meta else -74.97,
            "altitud": districts_meta[p.ubigeo].altitud_msnm if p.ubigeo in districts_meta else 3500,
        }
        for p in preds
    ]
)

col1, col2 = st.columns([1.4, 1])

with col1:
    prov_agg = (
        df_preds.groupby("provincia")
        .agg(
            dci_actual_mean=("dci_actual", "mean"),
            dci_proj_mean=("dci_proyectada", "mean"),
            dci_proj_max=("dci_proyectada", "max"),
        )
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(7.5, 4.2), dpi=130)
    x = np.arange(len(prov_agg["provincia"]))
    width = 0.26
    ax.bar(x - width, prov_agg["dci_actual_mean"], width, label="DCI Actual S3 (%)", color="#3498db")
    ax.bar(x, prov_agg["dci_proj_mean"], width, label="DCI Proyectada S4 (%)", color="#f39c12")
    ax.bar(x + width, prov_agg["dci_proj_max"], width, label="Máximo Distrital S4 (%)", color="#e74c3c")
    ax.axhline(25.0, color="#c0392b", linestyle="--", linewidth=1.5, label="Umbral Crítico S5 (25.0%)")
    ax.set_xticks(x)
    ax.set_xticklabels(prov_agg["provincia"], rotation=25, ha="right", fontsize=8.5)
    ax.set_ylabel("Prevalencia DCI (%)", fontsize=9)
    ax.set_title("Balance Homeostático S3–S4 por Provincia", fontsize=10, fontweight="bold")
    ax.legend(fontsize=7.5)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with col2:
    fig_map, ax_map = plt.subplots(figsize=(5.5, 4.2), dpi=130)
    sc = ax_map.scatter(
        df_preds["lon"],
        df_preds["lat"],
        c=df_preds["dci_proyectada"],
        cmap="RdYlGn_r",
        s=45 + (df_preds["dci_proyectada"] - 10).clip(lower=0) * 3,
        alpha=0.85,
        edgecolors="#2c3e50",
        linewidths=0.5,
    )
    cbar = plt.colorbar(sc, ax=ax_map)
    cbar.set_label("DCI Proyectada S4 (%)", fontsize=8)
    crit = df_preds[df_preds["algedonico"]]
    if not crit.empty:
        ax_map.scatter(crit["lon"], crit["lat"], facecolors="none", edgecolors="#8b0000", s=140, linewidths=1.6, label="Alerta S5 (>25%)")
        ax_map.legend(fontsize=7.5, loc="lower left")
    ax_map.set_title("Mapa Territorial de Riesgo (100 Distritos)", fontsize=10, fontweight="bold")
    ax_map.set_xlabel("Longitud", fontsize=8)
    ax_map.set_ylabel("Latitud", fontsize=8)
    ax_map.grid(True, linestyle="--", alpha=0.25)
    plt.tight_layout()
    st.pyplot(fig_map)
    plt.close(fig_map)

st.dataframe(
    df_preds[
        ["ubigeo", "provincia", "distrito", "red_salud", "altitud", "dci_actual", "dci_proyectada", "riesgo", "algedonico"]
    ].rename(
        columns={
            "ubigeo": "Ubigeo",
            "provincia": "Provincia",
            "distrito": "Distrito",
            "red_salud": "Red de Salud",
            "altitud": "Altitud (msnm)",
            "dci_actual": "DCI Actual S3 (%)",
            "dci_proyectada": "DCI Proyectada S4 (%)",
            "riesgo": "Nivel de Riesgo",
            "algedonico": "Supera Umbral Algedónico (25%)",
        }
    ),
    use_container_width=True,
)
