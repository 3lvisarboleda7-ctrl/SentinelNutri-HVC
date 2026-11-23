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

# Umbrales deterministas de la Regla Fija 4 (Equilibrio Axiológico PRVU — fuera del alcance del LLM)
ISDH_GEOM_CRITICAL_THRESHOLD: float = 0.45
ISDH_GEOM_ALERT_THRESHOLD: float = 0.52
AXIOLOGICAL_SIGMA_CRITICAL_THRESHOLD: float = 0.22
AXIOLOGICAL_SIGMA_MODERATE_THRESHOLD: float = 0.18
ESPEJISMO_SE_MIN: float = 0.85
ESPEJISMO_STRUCTURAL_MAX_JD: float = 0.40
ESPEJISMO_STRUCTURAL_MAX_CN: float = 0.35
PAN_EXECUTION_PENALTY_WARNING_PCT: float = 75.0

PRVU_OEI_GOVERNANCE_MAP: Dict[str, Dict[str, str]] = {
    "S": {
        "oei": "OEI.01 (Reducir DCI y Anemia) y OEI.03 (Salud Materno-Infantil)",
        "ods": "ODS 2 (Meta 2.2) y ODS 3 (Meta 3.2)",
        "sector": "DIRESA / Red de Salud Provincial",
        "accion": "Reforzar brigadas CRED, suplementación preventiva de hierro y consejería de lactancia materna exclusiva.",
    },
    "RM": {
        "oei": "OEI.08 (Competitividad Agraria) y OEI.01 (Articulación PAN 0001)",
        "ods": "ODS 1 (Fin de la Pobreza) y ODS 2 (Seguridad Alimentaria)",
        "sector": "DRA / GRDE / MEF (PAN 0001)",
        "accion": "Acelerar inversión productiva familiar y asignación per cápita del Programa Articulado Nutricional.",
    },
    "Se": {
        "oei": "OEI.03 (Protección Social e Inclusión) y OEI.01 (DCI)",
        "ods": "ODS 1 (Protección Social) y ODS 2 (Meta 2.2)",
        "sector": "MIDIS (Juntos, Cuna Más, Qali Warma) / GRDS",
        "accion": "Cerrar brechas de afiliación nominal del padrón infantil en Juntos, Cuna Más y Qali Warma.",
    },
    "CO": {
        "oei": "OEI.02 (Logros de Aprendizaje y Educación Materna) y OEI.01",
        "ods": "ODS 4 (Educación de Calidad) y ODS 5 (Igualdad de Género)",
        "sector": "DRE / UGEL / GRDS Huancavelica",
        "accion": "Activar alfabetización nutricional, educación secundaria rural femenina y sesiones demostrativas comunitarias.",
    },
    "JD": {
        "oei": "OEI.04 (Acceso a Agua Segura y Saneamiento Rural)",
        "ods": "ODS 6 (Meta 6.1: Agua Potable y Cloración Rural)",
        "sector": "DRVCS / Área Técnica Municipal (ATM) / JASS",
        "accion": "Intervenir sistemas rurales de cloración (cloro residual >= 0,5 mg/L) y mantenimiento preventivo de JASS.",
    },
    "CN": {
        "oei": "OEI.10 (Gestión del Riesgo de Desastres y Adaptación ante Heladas)",
        "ods": "ODS 13 (Acción por el Clima) y ODS 2 (Resiliencia Agroalimentaria)",
        "sector": "GRRNGMA / DRA / SENAMHI (Plan Multisectorial ante Heladas)",
        "accion": "Desplegar viviendas térmicas Sumaq Wasi, fitotoldos familiares y cobertizos previos al pico de heladas.",
    },
}


@dataclass(frozen=True)
class AxiologicalEquilibriumDecision:
    """
    Decisión determinista inmutable emitida por la Regla Fija 4 (Equilibrio Axiológico PRVU).
    Complementa la Regla Fija 2 (DCI > 25% -> S5) permitiendo detectar colapsos estructurales
    pre-algedónicos, espejismos asistenciales (Se alto con JD/CN colapsados) y cuellos de botella.
    """

    ubigeo: str
    distrito: str
    provincia: str
    estado_equilibrio_axiologico: str
    alerta_temprana_pre_algedonica: bool
    espejismo_asistencial_detectado: bool
    alerta_inejecucion_pan: bool
    brecha_horizontalizacion: float
    cuello_de_botella_prvu: str
    cuello_de_botella_label: str
    cuello_de_botella_valor: float
    dimension_dominante_prvu: str
    oei_prioritario: str
    ods_prioritario: str
    sector_prioritario: str
    accion_equilibradora_s3: str
    motivos_regla: Tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ubigeo": self.ubigeo,
            "distrito": self.distrito,
            "provincia": self.provincia,
            "estado_equilibrio_axiologico": self.estado_equilibrio_axiologico,
            "alerta_temprana_pre_algedonica": self.alerta_temprana_pre_algedonica,
            "espejismo_asistencial_detectado": self.espejismo_asistencial_detectado,
            "alerta_inejecucion_pan": self.alerta_inejecucion_pan,
            "brecha_horizontalizacion": round(self.brecha_horizontalizacion, 4),
            "cuello_de_botella_prvu": self.cuello_de_botella_prvu,
            "cuello_de_botella_label": self.cuello_de_botella_label,
            "cuello_de_botella_valor": round(self.cuello_de_botella_valor, 4),
            "dimension_dominante_prvu": self.dimension_dominante_prvu,
            "oei_prioritario": self.oei_prioritario,
            "ods_prioritario": self.ods_prioritario,
            "sector_prioritario": self.sector_prioritario,
            "accion_equilibradora_s3": self.accion_equilibradora_s3,
            "motivos_regla": list(self.motivos_regla),
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
        gov = evaluate_axiological_governance_rule(self)
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
            "brecha_horizontalizacion": round(gov.brecha_horizontalizacion, 4),
            "denominador_X_inejecucion_pan": round(self.denominador_X_inejecucion, 4),
            "isdh_hvc_arit": round(self.isdh_hvc_arit, 4),
            "isdh_hvc_geom": round(self.isdh_hvc_geom, 4),
            "isdh_hvc_arit_pct": round(self.isdh_hvc_arit * 100.0, 2),
            "isdh_hvc_geom_pct": round(self.isdh_hvc_geom * 100.0, 2),
            "cuello_de_botella_prvu": gov.cuello_de_botella_prvu,
            "estado_equilibrio_axiologico": gov.estado_equilibrio_axiologico,
            "espejismo_asistencial": gov.espejismo_asistencial_detectado,
            "alerta_pre_algedonica": gov.alerta_temprana_pre_algedonica,
            "alerta_inejecucion_pan": gov.alerta_inejecucion_pan,
            "oei_prioritario": gov.oei_prioritario,
        }


def evaluate_axiological_governance_rule(
    score: DistrictAxiologicalScore,
) -> AxiologicalEquilibriumDecision:
    """
    REGLA FIJA 4 (Equilibrio Axiológico y Abanico Equilibrador — Parra Luna, 2017, 2018):
    Evalúa de forma estrictamente determinista (fuera del LLM) si un distrito presenta:
    - Desequilibrio axiológico crítico (`isdh_hvc_geom < 0.45`, `sigma_Y >= 0.22` o espejismo severo).
    - Espejismo asistencial (`Se >= 0.85` coexistiendo con `JD < 0.40` o `CN < 0.35`).
    - Alerta temprana pre-algedónica (colapso axiológico crítico antes de superar DCI > 25%).
    - Brecha de horizontalización (`max(y_i) - min(y_i)`) y cuello de botella PRVU mapeado a OEI/ODS.
    """
    dim_map: Dict[str, float] = {
        "S": score.dim_S,
        "RM": score.dim_RM,
        "Se": score.dim_Se,
        "CO": score.dim_CO,
        "JD": score.dim_JD,
        "CN": score.dim_CN,
    }
    numeric_checks = [
        *dim_map.values(),
        score.isdh_hvc_geom,
        score.desequilibrio_sigma_Y,
        score.ejecucion_pan_mef_pct,
        score.tasa_dci_pct,
    ]
    if not all(math.isfinite(float(v)) for v in numeric_checks):
        raise ValueError(f"Valores axiológicos no finitos (NaN/Inf) para el ubigeo '{score.ubigeo}'.")

    min_dim = min(PRVU_DIMENSIONS, key=lambda d: dim_map[d])
    max_dim = max(PRVU_DIMENSIONS, key=lambda d: dim_map[d])
    brecha_horiz = dim_map[max_dim] - dim_map[min_dim]

    espejismo = (score.dim_Se >= ESPEJISMO_SE_MIN) and (
        score.dim_JD < ESPEJISMO_STRUCTURAL_MAX_JD or score.dim_CN < ESPEJISMO_STRUCTURAL_MAX_CN
    )
    inejecucion_pan = score.ejecucion_pan_mef_pct < PAN_EXECUTION_PENALTY_WARNING_PCT

    motivos: List[str] = []
    if score.isdh_hvc_geom < ISDH_GEOM_CRITICAL_THRESHOLD:
        motivos.append(
            f"ISDH-HVC geométrico crítico ({score.isdh_hvc_geom * 100:.2f}% < {ISDH_GEOM_CRITICAL_THRESHOLD * 100:.1f}%)"
        )
    elif score.isdh_hvc_geom < ISDH_GEOM_ALERT_THRESHOLD:
        motivos.append(
            f"ISDH-HVC geométrico en alerta ({score.isdh_hvc_geom * 100:.2f}% < {ISDH_GEOM_ALERT_THRESHOLD * 100:.1f}%)"
        )

    if score.desequilibrio_sigma_Y >= AXIOLOGICAL_SIGMA_CRITICAL_THRESHOLD:
        motivos.append(
            f"Desequilibrio axiológico severo (σ_Y={score.desequilibrio_sigma_Y:.4f} >= {AXIOLOGICAL_SIGMA_CRITICAL_THRESHOLD:.2f})"
        )
    elif score.desequilibrio_sigma_Y >= AXIOLOGICAL_SIGMA_MODERATE_THRESHOLD:
        motivos.append(
            f"Desequilibrio axiológico moderado (σ_Y={score.desequilibrio_sigma_Y:.4f} >= {AXIOLOGICAL_SIGMA_MODERATE_THRESHOLD:.2f})"
        )

    if espejismo:
        motivos.append(
            f"Espejismo asistencial (Se={score.dim_Se * 100:.1f}% frente a JD={score.dim_JD * 100:.1f}% y CN={score.dim_CN * 100:.1f}%)"
        )
    if inejecucion_pan:
        motivos.append(
            f"Penalización presupuestal PAN 0001 (Ejecución={score.ejecucion_pan_mef_pct:.1f}% < {PAN_EXECUTION_PENALTY_WARNING_PCT:.1f}%, X={score.denominador_X_inejecucion:.3f})"
        )

    if (
        score.isdh_hvc_geom < ISDH_GEOM_CRITICAL_THRESHOLD
        or score.desequilibrio_sigma_Y >= AXIOLOGICAL_SIGMA_CRITICAL_THRESHOLD
        or (espejismo and score.isdh_hvc_geom < 0.50)
    ):
        estado = "DESEQUILIBRIO_CRITICO_AXIOLOGICO"
    elif (
        score.isdh_hvc_geom < ISDH_GEOM_ALERT_THRESHOLD
        or score.desequilibrio_sigma_Y >= AXIOLOGICAL_SIGMA_MODERATE_THRESHOLD
        or espejismo
        or inejecucion_pan
    ):
        estado = "DESEQUILIBRIO_MODERADO"
    else:
        estado = "EQUILIBRADO"
        motivos.append("Perfil axiológico dentro de los umbrales de equilibrio sistémico regional")

    alerta_pre_algedonica = estado == "DESEQUILIBRIO_CRITICO_AXIOLOGICO" and score.tasa_dci_pct <= 25.0
    if alerta_pre_algedonica:
        motivos.append(
            f"Alerta temprana pre-algedónica (DCI={score.tasa_dci_pct:.2f}% <= 25.0% con colapso axiológico estructural)"
        )

    gov_info = PRVU_OEI_GOVERNANCE_MAP[min_dim]
    return AxiologicalEquilibriumDecision(
        ubigeo=score.ubigeo,
        distrito=score.distrito,
        provincia=score.provincia,
        estado_equilibrio_axiologico=estado,
        alerta_temprana_pre_algedonica=alerta_pre_algedonica,
        espejismo_asistencial_detectado=espejismo,
        alerta_inejecucion_pan=inejecucion_pan,
        brecha_horizontalizacion=brecha_horiz,
        cuello_de_botella_prvu=min_dim,
        cuello_de_botella_label=PRVU_DIMENSION_LABELS[min_dim],
        cuello_de_botella_valor=dim_map[min_dim],
        dimension_dominante_prvu=max_dim,
        oei_prioritario=gov_info["oei"],
        ods_prioritario=gov_info["ods"],
        sector_prioritario=gov_info["sector"],
        accion_equilibradora_s3=gov_info["accion"],
        motivos_regla=tuple(motivos),
    )


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
    decisions_2024 = [evaluate_axiological_governance_rule(s) for s in ranked_2024]

    bottleneck_freq: Dict[str, int] = {d: 0 for d in PRVU_DIMENSIONS}
    for dec in decisions_2024:
        bottleneck_freq[dec.cuello_de_botella_prvu] += 1

    pre_algedonic_list = [
        dec.to_dict() for dec in decisions_2024 if dec.alerta_temprana_pre_algedonica
    ]
    espejismo_list = [
        {
            "ubigeo": dec.ubigeo,
            "distrito": dec.distrito,
            "provincia": dec.provincia,
            "cuello_de_botella_prvu": dec.cuello_de_botella_prvu,
            "brecha_horizontalizacion": round(dec.brecha_horizontalizacion, 4),
            "estado_equilibrio_axiologico": dec.estado_equilibrio_axiologico,
            "oei_prioritario": dec.oei_prioritario,
        }
        for dec in decisions_2024
        if dec.espejismo_asistencial_detectado
    ]

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
        "reglas_axiologicas_gobernanza_2024": {
            "regla": "Regla Fija 4 (Equilibrio Axiológico PRVU y Abanico Equilibrador — Parra Luna)",
            "umbrales_fijos": {
                "isdh_geom_critico": ISDH_GEOM_CRITICAL_THRESHOLD,
                "isdh_geom_alerta": ISDH_GEOM_ALERT_THRESHOLD,
                "sigma_Y_critico": AXIOLOGICAL_SIGMA_CRITICAL_THRESHOLD,
                "sigma_Y_moderado": AXIOLOGICAL_SIGMA_MODERATE_THRESHOLD,
                "espejismo_Se_min": ESPEJISMO_SE_MIN,
                "espejismo_JD_max": ESPEJISMO_STRUCTURAL_MAX_JD,
                "espejismo_CN_max": ESPEJISMO_STRUCTURAL_MAX_CN,
                "ejecucion_pan_alerta_pct": PAN_EXECUTION_PENALTY_WARNING_PCT,
            },
            "resumen_estados_2024": {
                "equilibrados": sum(1 for d in decisions_2024 if d.estado_equilibrio_axiologico == "EQUILIBRADO"),
                "desequilibrio_moderado": sum(1 for d in decisions_2024 if d.estado_equilibrio_axiologico == "DESEQUILIBRIO_MODERADO"),
                "desequilibrio_critico": sum(1 for d in decisions_2024 if d.estado_equilibrio_axiologico == "DESEQUILIBRIO_CRITICO_AXIOLOGICO"),
                "espejismo_asistencial_count": len(espejismo_list),
                "alerta_pre_algedonica_count": len(pre_algedonic_list),
                "alerta_inejecucion_pan_count": sum(1 for d in decisions_2024 if d.alerta_inejecucion_pan),
            },
            "frecuencia_cuello_botella_prvu": bottleneck_freq,
            "distritos_alerta_pre_algedonica": pre_algedonic_list,
            "distritos_espejismo_asistencial": espejismo_list,
        },
        "top_5_isdh_2024": [s.to_dict() for s in ranked_2024[:5]],
        "bottom_5_isdh_2024": [s.to_dict() for s in ranked_2024[-5:]],
        "scores_2024": [s.to_dict() for s in ranked_2024],
    }
