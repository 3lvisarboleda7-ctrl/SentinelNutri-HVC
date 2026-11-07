"""
Pruebas Unitarias de las 3 Reglas Fijas Cibernéticas (Figura 1 - Recuadros Punteados):
1. Clasificación determinista de riesgo distrital.
2. Disparo obligatorio del Canal Algedónico hacia S5 cuando `DCI proyectada > 25 %`.
3. Bloqueo de publicación en el Canal de Control S3 hasta contar con Aprobación Humana (HITL).
"""

from sentinelnutri.domain.entities.alert_msv import ApprovalStatus, MSVChannel
from sentinelnutri.domain.entities.prediction import RiskLevel
from sentinelnutri.domain.rules.fixed_thresholds import (
    can_publish_to_s3_control,
    classify_risk_level,
    evaluate_fixed_algedonic_rule,
)


def test_algedonic_rule_triggers_s5_when_dci_above_25_percent() -> None:
    decision = evaluate_fixed_algedonic_rule(ubigeo="090206", dci_proyectada_pct=26.4)
    assert decision.supera_umbral_critico is True
    assert decision.canal_obligatorio == MSVChannel.S5_ALGEDONICO
    assert decision.requiere_alerta_inmediata_s5 is True


def test_algedonic_rule_routes_to_s3_when_dci_at_or_below_25_percent() -> None:
    decision = evaluate_fixed_algedonic_rule(ubigeo="090101", dci_proyectada_pct=19.8)
    assert decision.supera_umbral_critico is False
    assert decision.canal_obligatorio == MSVChannel.S3_CONTROL
    assert decision.requiere_alerta_inmediata_s5 is False


def test_risk_level_classification_tiers() -> None:
    assert classify_risk_level(27.1) == RiskLevel.CRITICO
    assert classify_risk_level(22.0) == RiskLevel.ALTO
    assert classify_risk_level(15.0) == RiskLevel.MODERADO
    assert classify_risk_level(10.5) == RiskLevel.BAJO


def test_human_in_the_loop_approval_gate_for_s3_control() -> None:
    assert can_publish_to_s3_control(ApprovalStatus.PENDIENTE_APROBACION) is False
    assert can_publish_to_s3_control(ApprovalStatus.RECHAZADO) is False
    assert can_publish_to_s3_control(ApprovalStatus.ALGEDONICO_DIRECTO_S5) is False
    assert can_publish_to_s3_control(ApprovalStatus.APROBADO_S3) is True

