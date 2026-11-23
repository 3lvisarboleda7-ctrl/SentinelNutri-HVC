"""
Calcula los indicadores axiológicos de Francisco Parra Luna (2017, 2018) y las reglas
deterministas de equilibrio axiológico (Regla Fija 4) sobre el panel histórico consolidado
de los 100 distritos de Huancavelica (2014–2024), delegando al servicio unificado
`export_parra_luna_artifacts` (Single Source of Truth):
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

from sentinelnutri.application.export_artifacts_service import export_parra_luna_artifacts


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

    result = export_parra_luna_artifacts(
        panel_rows=panel_rows,
        s5_ubigeos=s5_ubigeos,
        exports_dir=ROOT / "data/exports",
        figures_dir=ROOT / "docs/figures",
    )
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
