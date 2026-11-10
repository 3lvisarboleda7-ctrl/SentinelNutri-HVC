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
from tests.unit.test_catboost_shap_contract import (
    test_catboost_shap_local_additivity_and_s5_threshold,
)
from tests.unit.test_scrapers_and_ubigeo import (
    test_node_detector_identifies_equipo1_or_equipo2,
    test_sien_mef_midis_and_senamhi_parsers,
    test_ubigeo_harmonizer_covers_100_huancavelica_districts,
)
from tests.unit.test_adversarial_red_team import (
    test_red_team_1_privacy_guard_nested_and_variant_keys,
    test_red_team_2_boundary_and_corrupted_values_in_rules_and_predictor,
    test_red_team_3_persistence_referential_integrity_and_1100_rows_performance,
    test_red_team_4_fastapi_endpoints_and_hitl_security,
    test_red_team_5_llm_gateway_3_tier_failover_and_truncated_json,
    test_red_team_6_n8n_workflows_structural_and_rules_audit,
    test_red_team_7_dashboard_4_rooms_and_hitl_approver_guard,
    test_red_team_8_exported_artifacts_and_figures_integrity,
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
        ("Motor CatBoost + SHAP: Aditividad local y umbral S5 (>25%)", test_catboost_shap_local_additivity_and_s5_threshold),
        ("Infraestructura Dual: Detección automática Equipo 1 vs Equipo 2", test_node_detector_identifies_equipo1_or_equipo2),
        ("Armonizador ETL: Catálogo de los 100 distritos de Huancavelica", test_ubigeo_harmonizer_covers_100_huancavelica_districts),
        ("Scrapers Especializados: Parsers SIEN-HIS, MEF PAN, MIDIS y SENAMHI", test_sien_mef_midis_and_senamhi_parsers),
        ("Red-Team QA 1: Blindaje recursivo Ley N.° 29733 (anidados y variantes)", test_red_team_1_privacy_guard_nested_and_variant_keys),
        ("Red-Team QA 2: Límites exactos (25.0%) y rechazo de NaN/Inf en Reglas y CatBoost", test_red_team_2_boundary_and_corrupted_values_in_rules_and_predictor),
        ("Red-Team QA 3: Integridad referencial FK y rendimiento 1 100 filas SQLite/PG", test_red_team_3_persistence_referential_integrity_and_1100_rows_performance),
        ("Red-Team QA 4: Blindaje API FastAPI (SQLi, ubigeos 400/404, payloads 422 y HITL)", test_red_team_4_fastapi_endpoints_and_hitl_security),
        ("Red-Team QA 5: Failover de 3 niveles en LLM Gateway y recuperación JSON truncado", test_red_team_5_llm_gateway_3_tier_failover_and_truncated_json),
        ("Red-Team QA 6: Auditoría estructural de grafos y reglas en Workflows n8n", test_red_team_6_n8n_workflows_structural_and_rules_audit),
        ("Red-Team QA 7: Resiliencia de las 4 Salas del Dashboard Streamlit y guardia HITL S3", test_red_team_7_dashboard_4_rooms_and_hitl_approver_guard),
        ("Red-Team QA 8: Integridad de artefactos exportados (1 100 filas, OEI/ODS, AUC>=0.90 y 300 DPI)", test_red_team_8_exported_artifacts_and_figures_integrity),
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

    print(f"\n=== TODAS LAS PRUEBAS ({len(tests) + 1}/{len(tests) + 1}) PASARON EXITOSAMENTE EN EL EQUIPO 1 ===")


if __name__ == "__main__":
    main()
