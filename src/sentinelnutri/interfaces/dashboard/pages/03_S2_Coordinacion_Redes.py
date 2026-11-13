"""Vista 3 del Dashboard Streamlit: Coordinación S2 de las 7 Redes de Salud Provinciales."""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from sentinelnutri.interfaces.dashboard.app import init_services

st.set_page_config(page_title="Coordinación S2 | SentinelNutri-HVC", page_icon="🤝", layout="wide")
repo, _, _, _, _, _, _ = init_services()

st.header("🤝 Soporte a S2 (Coordinación): Las 7 Redes de Salud Provinciales y PEI 2020–2027")
st.caption("Evolución multianual 2014–2024, relación ejecución presupuestal PAN 0001 (MEF) vs. DCI y recomendaciones sectoriales.")

all_series = repo.get_historical_series(anio_inicio=2014, anio_fin=2024)
if all_series:
    df_series = pd.DataFrame(
        [
            {
                "anio": r.anio,
                "provincia": r.provincia,
                "distrito": r.distrito,
                "dci_pct": r.tasa_dci_pct,
                "ejecucion_pan": r.ejecucion_pan_mef_pct,
                "agua_cloro": r.agua_cloro_adecuado_pct,
                "heladas": r.dias_heladas_anual,
            }
            for r in all_series
        ]
    )

    col1, col2 = st.columns(2)
    with col1:
        fig_t, ax_t = plt.subplots(figsize=(6.8, 4.0), dpi=130)
        for prov, grp in df_series.groupby("provincia"):
            yearly = grp.groupby("anio")["dci_pct"].mean()
            ax_t.plot(yearly.index, yearly.values, marker="o", markersize=3.5, linewidth=1.6, label=prov)
        ax_t.axhline(25.0, color="#c0392b", linestyle="--", linewidth=1.3, label="Umbral S5 (25.0%)")
        ax_t.set_title("Evolución Histórica DCI por Red Provincial (2014–2024)", fontsize=9.5, fontweight="bold")
        ax_t.set_xlabel("Año", fontsize=8.5)
        ax_t.set_ylabel("DCI (%)", fontsize=8.5)
        ax_t.legend(fontsize=7, loc="upper right")
        ax_t.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig_t)
        plt.close(fig_t)

    with col2:
        df_2024 = df_series[df_series["anio"] == 2024]
        fig_s, ax_s = plt.subplots(figsize=(6.8, 4.0), dpi=130)
        sc = ax_s.scatter(
            df_2024["ejecucion_pan"],
            df_2024["dci_pct"],
            c=df_2024["agua_cloro"],
            cmap="viridis",
            alpha=0.8,
            edgecolors="#333333",
            linewidths=0.4,
        )
        cbar = plt.colorbar(sc, ax=ax_s)
        cbar.set_label("Agua con Cloro Adecuado (%)", fontsize=8)
        ax_s.axhline(25.0, color="#c0392b", linestyle="--", linewidth=1.2, label="Umbral S5 (25%)")
        ax_s.set_title("Ejecución PAN 0001 (MEF) vs. DCI Distrital (2024)", fontsize=9.5, fontweight="bold")
        ax_s.set_xlabel("% Ejecución Presupuestal PAN", fontsize=8.5)
        ax_s.set_ylabel("Tasa DCI (%)", fontsize=8.5)
        ax_s.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig_s)
        plt.close(fig_s)

st.subheader("Alertas y Recomendaciones Sectoriales Generadas (S2 / S3 / S5)")
alerts = repo.get_all_alerts()
st.dataframe(alerts, use_container_width=True)
