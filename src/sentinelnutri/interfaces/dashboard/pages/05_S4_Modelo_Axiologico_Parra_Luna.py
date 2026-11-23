"""Vista 5 del Dashboard Streamlit: Modelo Axiológico de Parra Luna (PRVU, ISDH-HVC y Regla Fija 4)."""

from dataclasses import asdict
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from sentinelnutri.domain.rules.parra_luna_axiological import (
    EXCLUDED_PRVU_DIMENSIONS,
    PRVU_DIMENSIONS,
    compute_parra_luna_scores,
    evaluate_axiological_governance_rule,
    summarize_parra_luna_panel,
)
from sentinelnutri.interfaces.dashboard.app import init_services

st.set_page_config(
    page_title="Modelo Axiológico Parra Luna (ISDH-HVC) | SentinelNutri-HVC",
    page_icon="📐",
    layout="wide",
)
repo, _, _, tool3, _, _, _ = init_services()

st.header("📐 Sala 5 · Modelo Axiológico de Parra Luna (PRVU, ISDH-HVC = Y / X y Regla Fija 4)")
st.caption(
    "Adaptación operativa de los valores universales (Parra Luna, 2017, 2018) a los 100 distritos de Huancavelica "
    "con 6 dimensiones pertinentes (S, RM, Se, CO, JD, CN), denominador transformador X = brecha de inejecución PAN 0001 "
    "y evaluación determinista de equilibrio axiológico (Regla Fija 4)."
)

series = repo.get_historical_series(anio_inicio=2014, anio_fin=2024)
preds = repo.get_latest_predictions()
if not preds:
    tool3.execute(anio_corte=2024)
    preds = repo.get_latest_predictions()

s5_ubigeos = [p.ubigeo for p in preds if p.supera_umbral_algedonico]
rows = [asdict(r) if not isinstance(r, dict) else r for r in series]
summary = summarize_parra_luna_panel(rows, s5_ubigeos=s5_ubigeos)
scores_all_objs = compute_parra_luna_scores(rows, reference_rows=rows)
score_obj_2024_by_ubigeo = {s.ubigeo: s for s in scores_all_objs if s.anio == 2024}

g2014 = summary["progreso_longitudinal"]["anio_2014"]
g2024 = summary["progreso_longitudinal"]["anio_2024"]
gs5 = summary["comparativo_2024_s5_vs_s3"]["distritos_s5_algedonicos"]
corr = summary["correlaciones_isdh_vs_dci"]
gov_ax = summary["reglas_axiologicas_gobernanza_2024"]["resumen_estados_2024"]

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "ISDH-HVC Aritmético 2024",
    f"{g2024['ISDH_HVC_arit'] * 100:.2f}%",
    f"+{(g2024['ISDH_HVC_arit'] - g2014['ISDH_HVC_arit']) * 100:.2f} pp vs 2014",
)
c2.metric(
    "ISDH-HVC Geométrico 2024",
    f"{g2024['ISDH_HVC_geom'] * 100:.2f}%",
    f"+{(g2024['ISDH_HVC_geom'] - g2014['ISDH_HVC_geom']) * 100:.2f} pp vs 2014",
)
c3.metric(
    "Desequilibrio Axiológico (σ_Y)",
    f"{g2024['sigma_Y']:.4f}",
    f"{g2024['sigma_Y'] - g2014['sigma_Y']:.4f} vs 2014",
    delta_color="inverse",
)
c4.metric(
    "Correlación Spearman (ISDH vs DCI)",
    f"{corr['corte_2024_spearman_rho']:.4f}",
    f"Pearson r = {corr['corte_2024_pearson_r']:.4f}",
)

st.markdown("#### Regla Fija 4 · Gobernanza de Equilibrio Axiológico y Abanico Equilibrador (Corte 2024)")
r1, r2, r3, r4 = st.columns(4)
r1.metric("Desequilibrio Crítico", f"{gov_ax['desequilibrio_critico']} distritos", help="ISDH_geom < 45% o σ_Y >= 0.22")
r2.metric("Espejismo Asistencial", f"{gov_ax['espejismo_asistencial_count']} distritos", help="Se >= 85% con JD < 40% o CN < 35%")
r3.metric("Alerta Pre-Algedónica", f"{gov_ax['alerta_pre_algedonica_count']} distritos", help="Colapso axiológico antes de superar DCI > 25%")
r4.metric("Penalización PAN < 75%", f"{gov_ax['alerta_inejecucion_pan_count']} distritos", help="Ejecución MEF PAN 0001 < 75% (X > 1.25)")

scores_2024 = summary["scores_2024"]
df_2024 = pd.DataFrame(scores_2024)
s5_set = set(s5_ubigeos)
df_2024["canal_msv"] = df_2024["ubigeo"].apply(lambda u: "S5_ALGEDONICO" if u in s5_set else "S3_CONTROL")

dist_options = {
    f"{r['ubigeo']} - {r['distrito']} ({r['provincia']}) | ISDH={r['isdh_hvc_geom_pct']:.1f}% [{r['estado_equilibrio_axiologico']}]": r
    for r in scores_2024
}
selected_label = st.selectbox(
    "Comparar un distrito específico contra el Perfil Regional 2024 y los Distritos Algedónicos S5:",
    options=list(dist_options.keys()),
    index=len(dist_options) - 1,
)
selected_row = dist_options[selected_label]
selected_dec = evaluate_axiological_governance_rule(score_obj_2024_by_ubigeo[selected_row["ubigeo"]])

if selected_dec.estado_equilibrio_axiologico == "DESEQUILIBRIO_CRITICO_AXIOLOGICO":
    st.error(
        f"**[{selected_dec.estado_equilibrio_axiologico}]** {selected_dec.distrito} ({selected_dec.provincia}) · "
        f"Cuello de botella PRVU: **{selected_dec.cuello_de_botella_label}** ({selected_dec.cuello_de_botella_valor * 100:.1f}%) · "
        f"Brecha de horizontalización: **{selected_dec.brecha_horizontalizacion * 100:.1f} pp** · "
        f"Prioridad: **{selected_dec.oei_prioritario}** ({selected_dec.sector_prioritario}).\n\n"
        f"**Acción equilibradora S3:** {selected_dec.accion_equilibradora_s3}"
    )
elif selected_dec.estado_equilibrio_axiologico == "DESEQUILIBRIO_MODERADO":
    st.warning(
        f"**[{selected_dec.estado_equilibrio_axiologico}]** {selected_dec.distrito} ({selected_dec.provincia}) · "
        f"Cuello de botella PRVU: **{selected_dec.cuello_de_botella_label}** ({selected_dec.cuello_de_botella_valor * 100:.1f}%) · "
        f"Brecha de horizontalización: **{selected_dec.brecha_horizontalizacion * 100:.1f} pp** · "
        f"Prioridad: **{selected_dec.oei_prioritario}**.\n\n"
        f"**Acción equilibradora S3:** {selected_dec.accion_equilibradora_s3}"
    )
else:
    st.success(
        f"**[{selected_dec.estado_equilibrio_axiologico}]** {selected_dec.distrito} ({selected_dec.provincia}) · "
        f"Brecha de horizontalización: **{selected_dec.brecha_horizontalizacion * 100:.1f} pp** · "
        f"Menor dimensión relativa: **{selected_dec.cuello_de_botella_label}** ({selected_dec.cuello_de_botella_valor * 100:.1f}%)."
    )

col_left, col_right = st.columns(2)
dim_labels = ["Salud (S)", "Riqueza (RM)", "Seguridad (Se)", "Conoc. (CO)", "Just. Dist. (JD)", "Adapt. Nat. (CN)"]
x = np.arange(len(PRVU_DIMENSIONS))

with col_left:
    fig1, ax1 = plt.subplots(figsize=(6.8, 4.3), dpi=130)
    v_sel = [
        selected_row["y1_salud_S"] * 100.0,
        selected_row["y2_riqueza_RM"] * 100.0,
        selected_row["y3_seguridad_Se"] * 100.0,
        selected_row["y4_conocimiento_CO"] * 100.0,
        selected_row["y6_justicia_distributiva_JD"] * 100.0,
        selected_row["y7_adaptacion_natural_CN"] * 100.0,
    ]
    v_2024 = [g2024[d] * 100.0 for d in PRVU_DIMENSIONS]
    v_s5 = [gs5[d] * 100.0 for d in PRVU_DIMENSIONS]
    v_2014 = [g2014[d] * 100.0 for d in PRVU_DIMENSIONS]

    ax1.plot(x, v_2024, marker="o", lw=2.3, color="#0f4c81", label=f"Promedio HVC 2024 ({g2024['ISDH_HVC_arit']*100:.1f}%)")
    ax1.plot(x, v_sel, marker="^", lw=2.2, color="#2e7d32", label=f"{selected_row['distrito']} ({selected_row['isdh_hvc_arit_pct']:.1f}%)")
    ax1.plot(x, v_s5, marker="s", lw=2.0, linestyle="--", color="#c62828", label=f"Críticos S5 (n={gs5['n']}, {gs5['ISDH_HVC_arit']*100:.1f}%)")
    ax1.plot(x, v_2014, marker="d", lw=1.4, linestyle=":", color="#757575", label=f"Línea Base 2014 ({g2014['ISDH_HVC_arit']*100:.1f}%)")

    ax1.set_xticks(x)
    ax1.set_xticklabels(dim_labels, fontsize=8)
    ax1.set_ylim(0, 105)
    ax1.set_ylabel("Realización Axiológica (%)")
    ax1.set_title("Perfil Axiológico PRVU Comparado (Parra Luna)", fontsize=10, fontweight="bold")
    ax1.grid(axis="y", linestyle="--", alpha=0.35)
    ax1.legend(fontsize=7.5, loc="lower right")
    plt.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

with col_right:
    provs = list(summary["provincias_2024"].keys())
    isdh_a = [summary["provincias_2024"][p]["ISDH_HVC_arit"] * 100.0 for p in provs]
    isdh_g = [summary["provincias_2024"][p]["ISDH_HVC_geom"] * 100.0 for p in provs]
    xp = np.arange(len(provs))
    w = 0.36
    fig2, ax2 = plt.subplots(figsize=(6.8, 4.3), dpi=130)
    ax2.bar(xp - w / 2, isdh_a, width=w, color="#1565c0", label="ISDH-HVC Aritmético (Y_arit / X)")
    ax2.bar(xp + w / 2, isdh_g, width=w, color="#00897b", label="ISDH-HVC Geométrico (Y_geom / X)")
    ax2.set_xticks(xp)
    ax2.set_xticklabels(provs, rotation=20, ha="right", fontsize=8.5)
    ax2.set_ylim(0, 80)
    ax2.set_ylabel("ISDH-HVC = Y / X (%)")
    ax2.set_title("Desarrollo Sistémico Nutricional por Provincia (2024)", fontsize=10, fontweight="bold")
    ax2.grid(axis="y", linestyle="--", alpha=0.35)
    ax2.legend(fontsize=8)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

st.subheader("Ranking Distrital 2024 — Modelo Axiológico de Parra Luna y Regla Fija 4 (100 Distritos)")
st.dataframe(
    df_2024[
        [
            "ubigeo",
            "provincia",
            "distrito",
            "canal_msv",
            "estado_equilibrio_axiologico",
            "cuello_de_botella_prvu",
            "espejismo_asistencial",
            "alerta_pre_algedonica",
            "tasa_dci_pct",
            "ejecucion_pan_mef_pct",
            "desequilibrio_axiologico_sigma",
            "brecha_horizontalizacion",
            "denominador_X_inejecucion_pan",
            "isdh_hvc_arit_pct",
            "isdh_hvc_geom_pct",
        ]
    ],
    use_container_width=True,
)

with st.expander("Criterios metodológicos de exclusión del PRVU (dimensiones no aplicables)"):
    for dim_name, reason in EXCLUDED_PRVU_DIMENSIONS.items():
        st.markdown(f"- **{dim_name}:** {reason}")
