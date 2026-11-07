"""
Ejecutor de la Suite Completa de Pruebas Unitarias e Integración de SentinelNutri-HVC.
Funciona directamente con la librería estándar en el Equipo 1 (o con pytest cuando está instalado).
"""

from pathlib import Path
import shutil
import tempfile

from tests.unit.test_fixed_thresholds import (
    test_algedonic_rule_routes_to_s3_when_dci_at_or_below_25_percent,
    test_algedonic_rule_triggers_s5_when_dci_above_25_percent,
    test_human_in_the_loop_approval_gate_for_s3_control,
    test_risk_level_classification_tiers,
)
from tests.unit.test_ethical_scraper_hash import (
    test_academic_user_agent_validation,
    test_robots_txt_compliance,
    test_sha256_hash_change_detection,
)
from tests.unit.test_privacy_ley29733 import (
    test_non_strict_privacy_guard_strips_nominal_fields_cleanly,
)
from sentinelnutri.domain.rules.privacy_guard import (
    PrivacyViolationError,
    sanitize_district_payload_for_llm,
)
from tests.integration.test_6_supervisor_tools_api import (
    test_full_supervisor_cycle_and_msv_channels,
)


def test_strict_privacy_guard_manual() -> None:
    contaminated = {"ubigeo": "090101", "dni": "12345678"}
    try:
        sanitize_district_payload_for_llm(contaminated, strict=True)
        raise AssertionError("Debió lanzar PrivacyViolationError")
    except PrivacyViolationError:
        pass


def main() -> None:
    tests = [
        ("Regla Fija 2: Canal Algedónico S5 (>25%)", test_algedonic_rule_triggers_s5_when_dci_above_25_percent),
        ("Regla Fija 2: Enrutamiento Canal S3 (<=25%)", test_algedonic_rule_routes_to_s3_when_dci_at_or_below_25_percent),
        ("Regla Fija 1: Clasificación de niveles de riesgo", test_risk_level_classification_tiers),
        ("Regla Fija 3: Aprobación Humana (HITL) para S3", test_human_in_the_loop_approval_gate_for_s3_control),
        ("Privacidad Ley N.° 29733: Rechazo estricto de datos nominales", test_strict_privacy_guard_manual),
        ("Privacidad Ley N.° 29733: Limpieza de campos nominales", test_non_strict_privacy_guard_strips_nominal_fields_cleanly),
        ("Ética de Scraping: Huella digital SHA-256", test_sha256_hash_change_detection),
        ("Ética de Scraping: Respeto a robots.txt", test_robots_txt_compliance),
        ("Ética de Scraping: User-Agent académico FIIS-UNI", test_academic_user_agent_validation),
    ]

    for name, fn in tests:
        fn()
        print(f"[PASS] {name}")

    tmp_dir = Path(tempfile.mkdtemp(prefix="sentinelnutri_test_"))
    try:
        test_full_supervisor_cycle_and_msv_channels(tmp_dir)
        print("[PASS] Integración E2E: Las 6 Herramientas del Agente Supervisor + Canales MSV (S2, S3, S3*, S4, S5)")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print("\n=== TODAS LAS PRUEBAS (10/10) PASARON EXITOSAMENTE EN EL EQUIPO 1 ===")


if __name__ == "__main__":
    main()

