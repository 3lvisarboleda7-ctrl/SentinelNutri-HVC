"""
CLI de Administración y Orquestación Local — SentinelNutri-HVC (Ejecutable desde Equipo 1 o Equipo 2).

Comandos:
- `whoami`: Detecta e imprime automáticamente si estás en el EQUIPO 1 (Estación de Desarrollo)
  o en el EQUIPO 2 (Servidor Local con SSD + HDD 1TB + GTX 1050).
- `bootstrap`: Inicializa la BD, ejecuta el Backfill Histórico (2014-2024), evalúa el motor CatBoost+SHAP
  y simula un ciclo completo del Agente Supervisor con las 6 herramientas y las 3 reglas fijas.
"""

import argparse
import json
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


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI de SentinelNutri-HVC")
    parser.add_argument(
        "command",
        choices=["whoami", "bootstrap", "export-artifacts"],
        help="Comando a ejecutar",
    )
    parser.add_argument("--env", default="dev", help="Entorno de ejecución")
    args = parser.parse_args()

    if args.command == "whoami":
        sys.exit(run_whoami())
    if args.command == "bootstrap":
        sys.exit(run_bootstrap())
    if args.command == "export-artifacts":
        summary = export_all_equipo1_artifacts()
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        sys.exit(0)


if __name__ == "__main__":
    main()
