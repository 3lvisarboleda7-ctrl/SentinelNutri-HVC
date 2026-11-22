"""
Calcula los indicadores axiológicos de Francisco Parra Luna (2017, 2018) sobre el
panel histórico consolidado de los 100 distritos de Huancavelica (2014–2024) y genera:
1. data/exports/indicadores_parra_luna_hvc_2024.csv
2. data/exports/resumen_parra_luna_hvc.json
3. docs/figures/fig5_perfil_axiologico_parra_luna_hvc.png (300 DPI)
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sentinelnutri.domain.rules.parra_luna_axiological import (
    PRVU_DIMENSIONS,
    summarize_parra_luna_panel,
)


def main() -> None:
    panel_path = ROOT / "data/exports/panel_distrital_hvc_2014_2024.csv"
    gov_path = ROOT / "data/exports/matriz_gobernanza_oei_ods_hvc.csv"

    with panel_path.open(encoding="utf-8") as f:
        panel_rows = list(csv.DictReader(f))

    s5_ubigeos = []
    if gov_path.exists():
        with gov_path.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                canal = r.get("canal_msv_destino") or r.get("canal_destino") or r.get("canal_msv") or ""
                if canal == "S5_ALGEDONICO":
                    s5_ubigeos.append(str(r["ubigeo"]))

    summary = summarize_parra_luna_panel(panel_rows, s5_ubigeos=s5_ubigeos)

    # 1. Exportar CSV 2024 (100 distritos)
    csv_out = ROOT / "data/exports/indicadores_parra_luna_hvc_2024.csv"
    scores_2024 = summary["scores_2024"]
    s5_set = set(s5_ubigeos)
    for row in scores_2024:
        row["canal_msv"] = "S5_ALGEDONICO" if row["ubigeo"] in s5_set else "S3_CONTROL"

    fieldnames = list(scores_2024[0].keys())
    with csv_out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scores_2024)

    # 2. Exportar JSON resumen (sin duplicar la lista entera de 100 filas para mantenerlo ligero)
    json_out = ROOT / "data/exports/resumen_parra_luna_hvc.json"
    summary_light = {k: v for k, v in summary.items() if k != "scores_2024"}
    summary_light["total_distritos_2024"] = len(scores_2024)
    json_out.write_text(json.dumps(summary_light, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 3. Generar Figura 5 (300 DPI): Perfil Axiológico Comparado + ISDH-HVC Provincial
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fig_out = ROOT / "docs/figures/fig5_perfil_axiologico_parra_luna_hvc.png"
    fig_out.parent.mkdir(parents=True, exist_ok=True)

    dim_labels = [
        "Salud\n(S · y1)",
        "Riqueza Mat.\n(RM · y2)",
        "Seguridad Soc.\n(Se · y3)",
        "Conocimiento\n(CO · y4)",
        "Justicia Dist.\n(JD · y6)",
        "Adapt. Natural\n(CN · y7)",
    ]
    x = np.arange(len(PRVU_DIMENSIONS))

    g2014 = summary["progreso_longitudinal"]["anio_2014"]
    g2024 = summary["progreso_longitudinal"]["anio_2024"]
    gs5 = summary["comparativo_2024_s5_vs_s3"]["distritos_s5_algedonicos"]
    top1 = summary["top_5_isdh_2024"][0]

    v2014 = [g2014[d] * 100.0 for d in PRVU_DIMENSIONS]
    v2024 = [g2024[d] * 100.0 for d in PRVU_DIMENSIONS]
    vs5 = [gs5[d] * 100.0 for d in PRVU_DIMENSIONS]
    vtop = [
        top1["y1_salud_S"] * 100.0,
        top1["y2_riqueza_RM"] * 100.0,
        top1["y3_seguridad_Se"] * 100.0,
        top1["y4_conocimiento_CO"] * 100.0,
        top1["y6_justicia_distributiva_JD"] * 100.0,
        top1["y7_adaptacion_natural_CN"] * 100.0,
    ]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.4), dpi=300)

    # Panel A: Perfil Axiológico (estilo Parra Luna 2018 Figs. 1-3)
    ax1.plot(x, vtop, marker="^", lw=2.0, linestyle="--", color="#2e7d32", label=f"Líder 2024: {top1['distrito']} (ISDH={top1['isdh_hvc_arit_pct']:.1f}%)")
    ax1.plot(x, v2024, marker="o", lw=2.6, color="#0f4c81", label=f"Promedio HVC 2024 (ISDH={g2024['ISDH_HVC_arit']*100:.1f}%)")
    ax1.plot(x, vs5, marker="s", lw=2.3, color="#c62828", label=f"Distritos Algedónicos S5 2024 (n={gs5['n']}, ISDH={gs5['ISDH_HVC_arit']*100:.1f}%)")
    ax1.plot(x, v2014, marker="d", lw=1.8, linestyle=":", color="#757575", label=f"Línea Base HVC 2014 (ISDH={g2014['ISDH_HVC_arit']*100:.1f}%)")

    for xi, yi in zip(x, v2024):
        ax1.annotate(f"{yi:.1f}%", (xi, yi), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=7.5, color="#0f4c81", fontweight="bold")
    for xi, yi in zip(x, vs5):
        ax1.annotate(f"{yi:.1f}%", (xi, yi), textcoords="offset points", xytext=(0, -12), ha="center", fontsize=7.5, color="#c62828")

    ax1.set_xticks(x)
    ax1.set_xticklabels(dim_labels, fontsize=8.5)
    ax1.set_ylim(0, 105)
    ax1.set_ylabel("Nivel de Realización Axiológica Estándar (%)", fontsize=9)
    ax1.set_title("A. Perfil Axiológico PRVU (Parra Luna, 2017–2018)\nHuancavelica: Progreso 2014–2024 y Brecha S5", fontsize=10, fontweight="bold")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)
    ax1.legend(loc="lower right", fontsize=7.5, frameon=True)

    # Panel B: ISDH-HVC (T = Y/X) por Provincia (Aritmético vs Geométrico)
    provs = list(summary["provincias_2024"].keys())
    isdh_a = [summary["provincias_2024"][p]["ISDH_HVC_arit"] * 100.0 for p in provs]
    isdh_g = [summary["provincias_2024"][p]["ISDH_HVC_geom"] * 100.0 for p in provs]
    xp = np.arange(len(provs))
    w = 0.36

    b1 = ax2.bar(xp - w / 2, isdh_a, width=w, color="#1565c0", label="ISDH-HVC Aritmético (Y_arit / X)")
    b2 = ax2.bar(xp + w / 2, isdh_g, width=w, color="#00897b", label="ISDH-HVC Geométrico (Y_geom / X)")
    for bars in (b1, b2):
        for bar in bars:
            h = bar.get_height()
            ax2.annotate(f"{h:.1f}%", (bar.get_x() + bar.get_width() / 2, h), textcoords="offset points", xytext=(0, 3), ha="center", fontsize=7)

    ax2.set_xticks(xp)
    ax2.set_xticklabels(provs, rotation=22, ha="right", fontsize=8.5)
    ax2.set_ylim(0, 80)
    ax2.set_ylabel("Índice Sistémico ISDH-HVC = Y / X (%)", fontsize=9)
    ax2.set_title("B. Grado de Desarrollo Sistémico Nutricional (T = Y/X)\npor Provincia — Corte 2024 (X = Brecha PAN 0001)", fontsize=10, fontweight="bold")
    ax2.grid(axis="y", linestyle="--", alpha=0.4)
    ax2.legend(loc="upper right", fontsize=8)

    fig.tight_layout()
    fig.savefig(fig_out, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(json.dumps(summary_light, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
