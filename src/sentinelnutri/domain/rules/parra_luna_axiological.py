"""
Módulo Axiológico e Indicadores Sistémicos de Francisco Parra Luna (2017, 2018)
adaptados al Sistema 4 del MSV en la Región Huancavelica (SentinelNutri-HVC).

Referencias base:
- Parra Luna, F. (2017). Un Modelo Axiológico para la gobernanza mundial.
  Revista Internacional de Sistemas (SESGE), 21(1), 26–37.
- Parra Luna, F. (Ed.). (2018). ¿Qué es el desarrollo? Hacia un Índice Sistémico
  de Desarrollo Humano (ISDH). Avances Sistémicos (SESGE), Año 1, N.º 3.

Selección fundamentada sobre el Patrón Referencial de Valores Universales (PRVU):
- 6 dimensiones pertinentes al propósito nutricional distrital (cero doble conteo):
  1. Salud Nutricional (S, y1)
  2. Riqueza Material (RM, y2)
  3. Seguridad Social (Se, y3)
  4. Conocimiento (CO, y4)
  5. Justicia Distributiva en Servicios Básicos (JD, y6)
  6. Adaptación al Entorno Natural (CN, y7)
- 3 dimensiones + 1 descartadas por no aplicar al nivel distrital ni al dominio DCI:
  Libertad (L, y5), Prestigio Moral (PM, y9), Poder (P) y Exportación de armas.
- Denominador transformador (T = Y / X):
  X = 1 + (100 - ejecucion_pan_mef_pct) / 100
  (penaliza la inejecución presupuestal del Programa Articulado Nutricional 0001).
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Dict, List, Mapping, Sequence, Tuple


PRVU_DIMENSIONS: Tuple[str, ...] = ("S", "RM", "Se", "CO", "JD", "CN")

PRVU_DIMENSION_LABELS: Dict[str, str] = {
    "S": "Salud Nutricional (y1)",
    "RM": "Riqueza Material (y2)",
    "Se": "Seguridad Social (y3)",
    "CO": "Conocimiento (y4)",
    "JD": "Justicia Distributiva (y6)",
    "CN": "Adaptación Natural (y7)",
}

# Cada indicador se define como (clave_en_panel, es_positivo)
# Si es_positivo=False, se invierte (valor_positivo = -valor o 100 - valor) antes de Min-Max.
PRVU_INDICATOR_MAP: Dict[str, List[Tuple[str, bool]]] = {
    "S": [
        ("tasa_dci_pct", False),
        ("tasa_anemia_pct", False),
        ("tasa_bajo_peso_pct", False),
        ("controles_cred_completo_pct", True),
        ("lactancia_materna_exclusiva_pct", True),
    ],
    "RM": [
        ("pobreza_monetaria_pct", False),
        ("presupuesto_pan_per_capita_soles", True),
    ],
    "Se": [
        ("cobertura_juntos_pct", True),
        ("cobertura_cuna_mas_pct", True),
        ("cobertura_qali_warma_pct", True),
    ],
    "CO": [
        ("educacion_materna_secundaria_pct", True),
    ],
    "JD": [
        ("agua_cloro_adecuado_pct", True),
        ("saneamiento_basico_pct", True),
    ],
    "CN": [
        ("dias_heladas_anual", False),
        ("temp_minima_promedio_c", True),
        ("precipitacion_anual_mm", True),
    ],
}

EXCLUDED_PRVU_DIMENSIONS: Dict[str, str] = {
    "L (Libertad, y5)": (
        "Libertad de prensa, población penitenciaria y presión fiscal nacional carecen "
        "de desagregación distrital operativa y vínculo directo con la alerta temprana de DCI."
    ),
    "PM (Prestigio Moral, y9)": (
        "Ayuda oficial al desarrollo (% PNB) y saldo migratorio internacional son "
        "indicadores macro-país inaplicables a gobiernos distritales de Huancavelica."
    ),
    "Poder (P, anexo 30+1)": (
        "PIB nacional y arsenal defensivo no corresponden a gestión nutricional subnacional."
    ),
    "X original (Exportación de armas)": (
        "Sustituido bajo el Principio de Maximización Transformadora (T=Y/X) por la "
        "brecha de inejecución presupuestal del PAN 0001: X = 1 + (100 - ejecucion_pan_mef_pct)/100."
    ),
}


@dataclass(frozen=True)
class DistrictAxiologicalScore:
    ubigeo: str
    anio: int
    provincia: str
    distrito: str
    red_salud: str
    tasa_dci_pct: float
    ejecucion_pan_mef_pct: float
    dim_S: float
    dim_RM: float
    dim_Se: float
    dim_CO: float
    dim_JD: float
    dim_CN: float
    indice_bruto_Y_arit: float
    indice_bruto_Y_geom: float
    desequilibrio_sigma_Y: float
    denominador_X_inejecucion: float
    isdh_hvc_arit: float
    isdh_hvc_geom: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ubigeo": self.ubigeo,
            "anio": self.anio,
            "provincia": self.provincia,
            "distrito": self.distrito,
            "red_salud": self.red_salud,
            "tasa_dci_pct": round(self.tasa_dci_pct, 2),
            "ejecucion_pan_mef_pct": round(self.ejecucion_pan_mef_pct, 2),
            "y1_salud_S": round(self.dim_S, 4),
            "y2_riqueza_RM": round(self.dim_RM, 4),
            "y3_seguridad_Se": round(self.dim_Se, 4),
            "y4_conocimiento_CO": round(self.dim_CO, 4),
            "y6_justicia_distributiva_JD": round(self.dim_JD, 4),
            "y7_adaptacion_natural_CN": round(self.dim_CN, 4),
            "indice_bruto_Y_arit": round(self.indice_bruto_Y_arit, 4),
            "indice_bruto_Y_geom": round(self.indice_bruto_Y_geom, 4),
            "desequilibrio_axiologico_sigma": round(self.desequilibrio_sigma_Y, 4),
            "denominador_X_inejecucion_pan": round(self.denominador_X_inejecucion, 4),
            "isdh_hvc_arit": round(self.isdh_hvc_arit, 4),
            "isdh_hvc_geom": round(self.isdh_hvc_geom, 4),
            "isdh_hvc_arit_pct": round(self.isdh_hvc_arit * 100.0, 2),
            "isdh_hvc_geom_pct": round(self.isdh_hvc_geom * 100.0, 2),
        }


def _to_positive(val: float, is_positive: bool) -> float:
    return val if is_positive else -val


def _minmax_bounds(
    rows: Sequence[Mapping[str, Any]],
) -> Dict[str, Tuple[float, float]]:
    bounds: Dict[str, Tuple[float, float]] = {}
    for indicators in PRVU_INDICATOR_MAP.values():
        for key, is_pos in indicators:
            vals = [_to_positive(float(r[key]), is_pos) for r in rows]
            bounds[key] = (min(vals), max(vals))
    return bounds


def _normalize(val: float, lo: float, hi: float) -> float:
    if hi <= lo:
        return 0.5
    return max(0.0, min(1.0, (val - lo) / (hi - lo)))


def compute_parra_luna_scores(
    rows: Sequence[Mapping[str, Any]],
    reference_rows: Sequence[Mapping[str, Any]] | None = None,
    geom_floor: float = 0.01,
) -> List[DistrictAxiologicalScore]:
    """
    Calcula el perfil axiológico (6 dimensiones del PRVU) y el ISDH-HVC (T = Y/X)
    para cada registro distrital.

    Si `reference_rows` se provee (por ejemplo, toda la serie 2014–2024), la
    normalización Min-Max se fija sobre esa referencia global, permitiendo medir
    el progreso axiológico temporal (2014 -> 2024) en una escala común [0, 1].
    """
    if not rows:
        return []

    ref = reference_rows if reference_rows is not None else rows
    bounds = _minmax_bounds(ref)
    results: List[DistrictAxiologicalScore] = []

    for row in rows:
        dim_values: Dict[str, float] = {}
        for dim, indicators in PRVU_INDICATOR_MAP.items():
            norm_vals = [
                _normalize(_to_positive(float(row[key]), is_pos), bounds[key][0], bounds[key][1])
                for key, is_pos in indicators
            ]
            dim_values[dim] = sum(norm_vals) / len(norm_vals)

        vec = [dim_values[d] for d in PRVU_DIMENSIONS]
        y_arit = sum(vec) / len(vec)
        # Media geométrica (Parra Luna 2018 / Caselles / PNUD 2010) con piso numérico suave
        y_geom = math.exp(sum(math.log(max(v, geom_floor)) for v in vec) / len(vec))
        variance = sum((v - y_arit) ** 2 for v in vec) / len(vec)
        sigma_y = math.sqrt(variance)

        ejec_pan = max(0.0, min(100.0, float(row["ejecucion_pan_mef_pct"])))
        brecha_inejecucion_pct = 100.0 - ejec_pan
        x_denom = 1.0 + (brecha_inejecucion_pct / 100.0)

        results.append(
            DistrictAxiologicalScore(
                ubigeo=str(row["ubigeo"]),
                anio=int(row["anio"]),
                provincia=str(row.get("provincia", "")),
                distrito=str(row.get("distrito", "")),
                red_salud=str(row.get("red_salud", "")),
                tasa_dci_pct=float(row["tasa_dci_pct"]),
                ejecucion_pan_mef_pct=ejec_pan,
                dim_S=dim_values["S"],
                dim_RM=dim_values["RM"],
                dim_Se=dim_values["Se"],
                dim_CO=dim_values["CO"],
                dim_JD=dim_values["JD"],
                dim_CN=dim_values["CN"],
                indice_bruto_Y_arit=y_arit,
                indice_bruto_Y_geom=y_geom,
                desequilibrio_sigma_Y=sigma_y,
                denominador_X_inejecucion=x_denom,
                isdh_hvc_arit=y_arit / x_denom,
                isdh_hvc_geom=y_geom / x_denom,
            )
        )

    return results


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0.0 or dy == 0.0:
        return 0.0
    return num / (dx * dy)


def _ranks(vals: Sequence[float]) -> List[float]:
    indexed = sorted(enumerate(vals), key=lambda t: t[1])
    ranks = [0.0] * len(vals)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg_rank
        i = j + 1
    return ranks


def spearman_correlation(xs: Sequence[float], ys: Sequence[float]) -> float:
    return _pearson(_ranks(xs), _ranks(ys))


def summarize_parra_luna_panel(
    panel_rows: Sequence[Mapping[str, Any]],
    s5_ubigeos: Sequence[str] | None = None,
) -> Dict[str, Any]:
    """
    Genera el resumen estadístico completo sobre el panel 2014–2024:
    - Progreso axiológico longitudinal 2014 vs 2024 (escala común 2014–2024).
    - Perfil axiológico 2024 por provincia y comparativo S5 (>25%) vs S3 (<=25%).
    - Correlaciones Pearson y Spearman entre ISDH-HVC y tasa_dci_pct.
    """
    scores_all = compute_parra_luna_scores(panel_rows, reference_rows=panel_rows)
    scores_2014 = [s for s in scores_all if s.anio == 2014]
    scores_2024 = [s for s in scores_all if s.anio == 2024]

    def _agg_group(group: Sequence[DistrictAxiologicalScore]) -> Dict[str, float]:
        if not group:
            return {}
        n = len(group)
        return {
            "n": n,
            "S": round(sum(s.dim_S for s in group) / n, 4),
            "RM": round(sum(s.dim_RM for s in group) / n, 4),
            "Se": round(sum(s.dim_Se for s in group) / n, 4),
            "CO": round(sum(s.dim_CO for s in group) / n, 4),
            "JD": round(sum(s.dim_JD for s in group) / n, 4),
            "CN": round(sum(s.dim_CN for s in group) / n, 4),
            "Y_arit": round(sum(s.indice_bruto_Y_arit for s in group) / n, 4),
            "Y_geom": round(sum(s.indice_bruto_Y_geom for s in group) / n, 4),
            "sigma_Y": round(sum(s.desequilibrio_sigma_Y for s in group) / n, 4),
            "X_inejecucion": round(sum(s.denominador_X_inejecucion for s in group) / n, 4),
            "ISDH_HVC_arit": round(sum(s.isdh_hvc_arit for s in group) / n, 4),
            "ISDH_HVC_geom": round(sum(s.isdh_hvc_geom for s in group) / n, 4),
            "dci_media_pct": round(sum(s.tasa_dci_pct for s in group) / n, 2),
        }

    s5_set = set(s5_ubigeos or [])
    if s5_set:
        grp_s5 = [s for s in scores_2024 if s.ubigeo in s5_set]
        grp_s3 = [s for s in scores_2024 if s.ubigeo not in s5_set]
    else:
        grp_s5 = [s for s in scores_2024 if s.tasa_dci_pct > 25.0]
        grp_s3 = [s for s in scores_2024 if s.tasa_dci_pct <= 25.0]

    by_prov: Dict[str, List[DistrictAxiologicalScore]] = {}
    for s in scores_2024:
        by_prov.setdefault(s.provincia, []).append(s)
    prov_summary = {prov: _agg_group(items) for prov, items in sorted(by_prov.items())}

    ranked_2024 = sorted(scores_2024, key=lambda s: s.isdh_hvc_arit, reverse=True)
    r_all = _pearson([s.isdh_hvc_arit for s in scores_all], [s.tasa_dci_pct for s in scores_all])
    rho_all = spearman_correlation([s.isdh_hvc_arit for s in scores_all], [s.tasa_dci_pct for s in scores_all])
    r_2024 = _pearson([s.isdh_hvc_arit for s in scores_2024], [s.tasa_dci_pct for s in scores_2024])
    rho_2024 = spearman_correlation([s.isdh_hvc_arit for s in scores_2024], [s.tasa_dci_pct for s in scores_2024])

    return {
        "marco_teorico": "Parra Luna (2017, 2018) — PRVU e ISDH adaptado a Huancavelica (ISDH-HVC = Y / X)",
        "dimensiones_incluidas": {d: PRVU_DIMENSION_LABELS[d] for d in PRVU_DIMENSIONS},
        "dimensiones_descartadas": EXCLUDED_PRVU_DIMENSIONS,
        "progreso_longitudinal": {
            "anio_2014": _agg_group(scores_2014),
            "anio_2024": _agg_group(scores_2024),
        },
        "comparativo_2024_s5_vs_s3": {
            "distritos_s5_algedonicos": _agg_group(grp_s5),
            "distritos_s3_control": _agg_group(grp_s3),
        },
        "provincias_2024": prov_summary,
        "correlaciones_isdh_vs_dci": {
            "serie_2014_2024_pearson_r": round(r_all, 4),
            "serie_2014_2024_spearman_rho": round(rho_all, 4),
            "corte_2024_pearson_r": round(r_2024, 4),
            "corte_2024_spearman_rho": round(rho_2024, 4),
        },
        "top_5_isdh_2024": [s.to_dict() for s in ranked_2024[:5]],
        "bottom_5_isdh_2024": [s.to_dict() for s in ranked_2024[-5:]],
        "scores_2024": [s.to_dict() for s in ranked_2024],
    }
