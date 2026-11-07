"""
Reglas Fijas del Módulo Agéntico (Figura 1 del Perfil de Proyecto - Recuadros Punteados).

Tres decisiones quedan estrictamente fuera del alcance del modelo de lenguaje (LLM):
1. La predicción numérica: la calcula CatBoost (/predict) y nunca el LLM.
2. El disparo del canal algedónico: regla fija determinista (DCI proyectada > 25% -> S5 siempre).
3. La decisión final hacia S3: requiere aprobación explícita de un responsable humano (HITL).
"""

from dataclasses import dataclass
from sentinelnutri.domain.entities.alert_msv import ApprovalStatus, MSVChannel
from sentinelnutri.domain.entities.prediction import RiskLevel

ALGEDONIC_DCI_THRESHOLD_PCT: float = 25.0


@dataclass(frozen=True)
class AlgedonicRouteDecision:
    """Decisión inmutable emitida por la Regla Fija de Umbral de Riesgo (Nodo IF)."""

    ubigeo: str
    dci_proyectada_pct: float
    threshold_pct: float
    supera_umbral_critico: bool
    canal_obligatorio: MSVChannel
    requiere_alerta_inmediata_s5: bool
    requiere_aprobacion_humana_previa_s3: bool


def classify_risk_level(dci_proyectada_pct: float, threshold_pct: float = ALGEDONIC_DCI_THRESHOLD_PCT) -> RiskLevel:
    """Clasifica de forma determinista el nivel de riesgo de DCI proyectada por distrito."""
    if dci_proyectada_pct > threshold_pct:
        return RiskLevel.CRITICO
    if dci_proyectada_pct >= 20.0:
        return RiskLevel.ALTO
    if dci_proyectada_pct >= 12.1:  # Promedio nacional de referencia (12,1 %)
        return RiskLevel.MODERADO
    return RiskLevel.BAJO


def evaluate_fixed_algedonic_rule(
    ubigeo: str,
    dci_proyectada_pct: float,
    threshold_pct: float = ALGEDONIC_DCI_THRESHOLD_PCT,
) -> AlgedonicRouteDecision:
    """
    REGLA FIJA 2 (Canal Algedónico Automatizado S1/S4 -> S5):
    Si la DCI proyectada supera el umbral crítico (25 %), la señal se eleva directamente
    al S5 (Consejo Regional) por Telegram y Gmail sin que el LLM pueda omitirla.
    """
    is_critical = float(dci_proyectada_pct) > float(threshold_pct)
    if is_critical:
        return AlgedonicRouteDecision(
            ubigeo=ubigeo,
            dci_proyectada_pct=float(dci_proyectada_pct),
            threshold_pct=float(threshold_pct),
            supera_umbral_critico=True,
            canal_obligatorio=MSVChannel.S5_ALGEDONICO,
            requiere_alerta_inmediata_s5=True,
            requiere_aprobacion_humana_previa_s3=True,
        )
    return AlgedonicRouteDecision(
        ubigeo=ubigeo,
        dci_proyectada_pct=float(dci_proyectada_pct),
        threshold_pct=float(threshold_pct),
        supera_umbral_critico=False,
        canal_obligatorio=MSVChannel.S3_CONTROL,
        requiere_alerta_inmediata_s5=False,
        requiere_aprobacion_humana_previa_s3=True,
    )


def can_publish_to_s3_control(approval_status: ApprovalStatus) -> bool:
    """
    REGLA FIJA 3 (Aprobación Humana HITL -> Canal de Control S3):
    Las recomendaciones solo llegan al S3 (Gerencia Regional de Desarrollo Social)
    después de ser aprobadas por un responsable humano en Telegram o Gmail (Clavijo, 2026).
    """
    return approval_status == ApprovalStatus.APROBADO_S3

