"""Pruebas unitarias del módulo axiológico de Francisco Parra Luna (PRVU e ISDH-HVC)."""

import csv
from pathlib import Path

from sentinelnutri.domain.rules.parra_luna_axiological import (
    EXCLUDED_PRVU_DIMENSIONS,
    PRVU_DIMENSIONS,
    compute_parra_luna_scores,
    summarize_parra_luna_panel,
)


def test_parra_luna_prvu_selection_and_isdh_hvc_bounds() -> None:
    assert PRVU_DIMENSIONS == ("S", "RM", "Se", "CO", "JD", "CN")
    assert len(EXCLUDED_PRVU_DIMENSIONS) == 4

    panel_path = Path("data/exports/panel_distrital_hvc_2014_2024.csv")
    gov_path = Path("data/exports/matriz_gobernanza_oei_ods_hvc.csv")
    assert panel_path.exists()

    with panel_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    s5_ubigeos = []
    if gov_path.exists():
        with gov_path.open(encoding="utf-8") as f:
            s5_ubigeos = [r["ubigeo"] for r in csv.DictReader(f) if r.get("canal_msv_destino") == "S5_ALGEDONICO"]

    scores = compute_parra_luna_scores(rows, reference_rows=rows)
    assert len(scores) == 1100
    for s in scores:
        assert 0.0 <= s.indice_bruto_Y_arit <= 1.0
        assert 0.0 <= s.indice_bruto_Y_geom <= 1.0
        assert 1.0 <= s.denominador_X_inejecucion <= 2.0
        assert 0.0 <= s.isdh_hvc_arit <= s.indice_bruto_Y_arit + 1e-9
        assert s.isdh_hvc_geom <= s.isdh_hvc_arit + 1e-6

    summary = summarize_parra_luna_panel(rows, s5_ubigeos=s5_ubigeos)
    prog = summary["progreso_longitudinal"]
    assert prog["anio_2024"]["ISDH_HVC_arit"] > prog["anio_2014"]["ISDH_HVC_arit"]
    assert prog["anio_2024"]["sigma_Y"] < prog["anio_2014"]["sigma_Y"]

    cmp_s5 = summary["comparativo_2024_s5_vs_s3"]
    assert cmp_s5["distritos_s5_algedonicos"]["n"] == 5
    assert cmp_s5["distritos_s5_algedonicos"]["ISDH_HVC_geom"] < cmp_s5["distritos_s3_control"]["ISDH_HVC_geom"]
    assert cmp_s5["distritos_s5_algedonicos"]["sigma_Y"] > cmp_s5["distritos_s3_control"]["sigma_Y"]
    assert summary["correlaciones_isdh_vs_dci"]["corte_2024_spearman_rho"] < -0.90

    fig5 = Path("docs/figures/fig5_perfil_axiologico_parra_luna_hvc.png")
    assert fig5.exists() and fig5.stat().st_size > 20_000
