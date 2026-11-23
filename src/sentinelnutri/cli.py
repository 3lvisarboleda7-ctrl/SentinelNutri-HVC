"""
CLI de Administración y Orquestación Local — SentinelNutri-HVC (Ejecutable desde Equipo 1 o Equipo 2).

Comandos:
- `whoami`: Detecta e imprime automáticamente si estás en el EQUIPO 1 (Estación de Desarrollo)
  o en el EQUIPO 2 (Servidor Local con SSD + HDD 1TB + GTX 1050).
- `bootstrap`: Inicializa la BD, ejecuta el Backfill Histórico (2014-2024), evalúa el motor CatBoost+SHAP
  y simula un ciclo completo del Agente Supervisor con las 6 herramientas y las 3 reglas fijas.
"""

from dataclasses import asdict
import argparse
import json
import os
from pathlib import Path
import sys

from sentinelnutri.application import (
    Tool1ExtraerFuentesUseCase,
    Tool2ConsultarBdUseCase,
    Tool3PredecirRiesgoUseCase,
    Tool4ExplicarRiesgoUseCase,
    Tool5RedactarInformeUseCase,
    Tool6NotificarUseCase,
)
from sentinelnutri.application.export_artifacts_service import export_all_equipo1_artifacts
from sentinelnutri.config import detect_current_node
from sentinelnutri.domain.rules.fixed_thresholds import ALGEDONIC_DCI_THRESHOLD_PCT
from sentinelnutri.domain.rules.parra_luna_axiological import summarize_parra_luna_panel
from sentinelnutri.infrastructure.ml_xai import CatBoostShapPredictor
from sentinelnutri.infrastructure.notifications import (
    GmailNotificationAdapter,
    TelegramNotificationAdapter,
)
from sentinelnutri.infrastructure.persistence import (
    SqlAlchemyRepository,
    create_db_engine_and_session,
)
from sentinelnutri.infrastructure.scrapers import MultiSourceScraperOrchestrator


def run_whoami() -> int:
    node = detect_current_node()
    print(json.dumps(node.to_dict(), ensure_ascii=False, indent=2))
    return 0


def run_bootstrap() -> int:
    node = detect_current_node()
    print(f"=== [NODO DETECTADO: {node.node_id}] {node.role_name} ===")
    print(f"    Hostname: {node.hostname} | Detección: {node.detection_method}")
    _, session_factory = create_db_engine_and_session()
    repo = SqlAlchemyRepository(session_factory)
    scraper = MultiSourceScraperOrchestrator(repository=repo, raw_data_dir=node.active_raw_data_dir)
    predictor = CatBoostShapPredictor()
    telegram = TelegramNotificationAdapter()
    gmail = GmailNotificationAdapter()

    tool1 = Tool1ExtraerFuentesUseCase(repo, scraper)
    tool2 = Tool2ConsultarBdUseCase(repo)
    tool3 = Tool3PredecirRiesgoUseCase(repo, predictor)
    tool4 = Tool4ExplicarRiesgoUseCase(repo, predictor)
    tool5 = Tool5RedactarInformeUseCase()
    tool6 = Tool6NotificarUseCase(repo, telegram_notifier=telegram, gmail_notifier=gmail)

    print("=== [1/5] Ejecutando Herramienta 1 (`extraer_fuentes` en modo backfill 2014-2024) ===")
    res1 = tool1.execute(mode="backfill", start_year=2014, end_year=2024, force_rebuild=True)
    print(f"Portales consultados: {res1['portales_consultados']} | Registros integrados: {res1['registros_distritales_integrados']}")

    print("=== [2/5] Ejecutando Herramienta 2 (`consultar_bd`) ===")
    res2 = tool2.execute(anio_inicio=2014, anio_fin=2024)
    print(f"Distritos en catálogo (7 provincias): {res2['total_distritos_catalogo']} | Series: {res2['total_registros_serie']}")

    print("=== [3/5] Validando Motor CatBoost + SHAP (2014-2024) ===")
    all_series = repo.get_historical_series(anio_inicio=2014, anio_fin=2024)
    eval_metrics = predictor.train_and_evaluate(all_series)
    print("Métricas de validación:", json.dumps(eval_metrics["metricas_globales"], ensure_ascii=False))

    print("=== [4/5] Ejecutando Herramienta 3 (`predecir_riesgo`) y Regla Fija Algedónica (> 25%) ===")
    res3 = tool3.execute(anio_corte=2024)
    print(f"Distritos evaluados: {res3['total_distritos_evaluados']} | Alertas críticas S5 (>25%): {res3['total_alertas_algedonicas_s5']}")

    print("=== [5/5] Ejecutando Herramientas 4, 5 y 6 (`explicar_riesgo`, `redactar_informe`, `notificar`) ===")
    top_district = res3["predicciones_distritales"][0]["ubigeo"]
    exp = tool4.execute(top_district)
    rep = tool5.execute(exp)
    notif = tool6.execute_dispatch(rep["informe"])
    print("Resultado de enrutamiento MSV:", json.dumps(notif, ensure_ascii=False, indent=2))
    return 0


def _load_node_env_dict(env_file_path: str) -> dict[str, str]:
    values: dict[str, str] = {}
    p = Path(env_file_path)
    if p.exists():
        for raw_line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            values[k.strip()] = v.strip().strip('"')
    return values


def run_verify_env() -> int:
    node = detect_current_node()
    actual_env_path = node.recommended_env_file.replace(".example", "")
    file_env = _load_node_env_dict(actual_env_path)

    def _has_var(key: str) -> bool:
        val = (os.getenv(key) or file_env.get(key) or "").strip()
        return bool(val and not val.lower().startswith("tu_") and "placeholder" not in val.lower())

    checks = {
        "node_id": node.node_id,
        "recommended_env_file": actual_env_path,
        "env_file_exists": Path(actual_env_path).exists(),
        "GEMINI_API_KEY": "CONFIGURADO" if _has_var("GEMINI_API_KEY") else "PENDIENTE (Usando plantilla/fallback)",
        "TELEGRAM_BOT_TOKEN": "CONFIGURADO" if _has_var("TELEGRAM_BOT_TOKEN") else "SIMULACION_LOCAL (Dry-Run)",
        "GMAIL_APP_PASSWORD": "CONFIGURADO" if _has_var("GMAIL_APP_PASSWORD") else "SIMULACION_LOCAL (Dry-Run)",
        "CLOUDFLARE_TUNNEL_TOKEN": "CONFIGURADO" if _has_var("CLOUDFLARE_TUNNEL_TOKEN") else "PENDIENTE_EN_EQUIPO_2",
        "OLLAMA_BASE_URL": os.getenv("OLLAMA_BASE_URL") or file_env.get("OLLAMA_BASE_URL") or "http://localhost:11434",
    }
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    return 0


def run_audit_governance() -> int:
    """Ejecuta desde terminal la auditoría consolidada de las 4 Reglas Fijas, Parra Luna y huellas SHA-256."""
    _, session_factory = create_db_engine_and_session()
    repo = SqlAlchemyRepository(session_factory)
    scraper = MultiSourceScraperOrchestrator(repository=repo)
    predictor = CatBoostShapPredictor()
    tool1 = Tool1ExtraerFuentesUseCase(repo, scraper)
    tool3 = Tool3PredecirRiesgoUseCase(repo, predictor)

    records = repo.get_historical_series(anio_inicio=2014, anio_fin=2024)
    if not records:
        tool1.execute(mode="backfill", start_year=2014, end_year=2024, force_rebuild=True)
        records = repo.get_historical_series(anio_inicio=2014, anio_fin=2024)
    preds = repo.get_latest_predictions()
    if not preds:
        tool3.execute(anio_corte=2024)
        preds = repo.get_latest_predictions()

    alerts = repo.get_all_alerts()
    loads = repo.get_recent_loads(limit=100)
    s5_ubigeos = [p.ubigeo for p in preds if p.supera_umbral_algedonico]
    rows = [asdict(r) if not isinstance(r, dict) else r for r in records]
    pl = summarize_parra_luna_panel(rows, s5_ubigeos=s5_ubigeos)
    ax_gov = pl["reglas_axiologicas_gobernanza_2024"]

    report = {
        "sistema": "SentinelNutri-HVC (Auditoría CLI de Gobernanza Cibernética y Axiológica)",
        "reglas_fijas_activas": {
            "regla_1_prediccion": "CatBoost+SHAP exclusivo (/predict)",
            "regla_2_umbral_algedonico_s5_pct": ALGEDONIC_DCI_THRESHOLD_PCT,
            "regla_3_compuerta_hitl_s3": "Aprobación humana nominal obligatoria + huella SHA-256",
            "regla_4_equilibrio_axiologico_parra_luna": ax_gov["regla"],
        },
        "distritos_s5_algedonicos_2024": len(s5_ubigeos),
        "gobernanza_axiologica_2024": ax_gov["resumen_estados_2024"],
        "frecuencia_cuello_botella_prvu": ax_gov["frecuencia_cuello_botella_prvu"],
        "alertas_auditadas_bd": {
            "total": len(alerts),
            "con_huella_auditoria_sha256": sum(1 for a in alerts if a.get("huella_auditoria_sha256")),
            "con_huella_resolucion_sha256": sum(1 for a in alerts if a.get("huella_resolucion_sha256")),
        },
        "cargas_auditadas_sha256": len(loads),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI de SentinelNutri-HVC")
    parser.add_argument(
        "command",
        choices=["whoami", "verify-env", "bootstrap", "export-artifacts", "audit-governance"],
        help="Comando a ejecutar",
    )
    parser.add_argument("--env", default="dev", help="Entorno de ejecución")
    args = parser.parse_args()

    if args.command == "whoami":
        sys.exit(run_whoami())
    if args.command == "verify-env":
        sys.exit(run_verify_env())
    if args.command == "bootstrap":
        sys.exit(run_bootstrap())
    if args.command == "export-artifacts":
        summary = export_all_equipo1_artifacts()
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        sys.exit(0)
    if args.command == "audit-governance":
        sys.exit(run_audit_governance())


if __name__ == "__main__":
    main()
