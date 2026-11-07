"""
Pruebas de Integración Extremo a Extremo de las 6 Herramientas del Agente Supervisor (Tabla 5)
y de los Canales del Modelo de Sistema Viable (S2, S3, S3*, S4 y S5).
"""

from pathlib import Path
from sentinelnutri.application import (
    Tool1ExtraerFuentesUseCase,
    Tool2ConsultarBdUseCase,
    Tool3PredecirRiesgoUseCase,
    Tool4ExplicarRiesgoUseCase,
    Tool5RedactarInformeUseCase,
    Tool6NotificarUseCase,
)
from sentinelnutri.infrastructure.ml_xai import CatBoostShapPredictor
from sentinelnutri.infrastructure.notifications import (
    GmailNotificationAdapter,
    TelegramNotificationAdapter,
)
from sentinelnutri.infrastructure.persistence import (
    SqlAlchemyRepository,
    create_db_engine_and_session,
)
from sentinelnutri.infrastructure.scrapers import (
    EthicalWebScraperClient,
    MultiSourceScraperOrchestrator,
)


def test_full_supervisor_cycle_and_msv_channels(tmp_path: Path) -> None:
    db_path = tmp_path / "test_sentinelnutri.db"
    raw_dir = tmp_path / "hdd_raw"

    _, session_factory = create_db_engine_and_session(f"sqlite:///{db_path}")
    repo = SqlAlchemyRepository(session_factory)
    scraper_client = EthicalWebScraperClient(raw_storage_dir=str(raw_dir), rate_limit_seconds=0.0)
    scraper = MultiSourceScraperOrchestrator(repository=repo, scraper_client=scraper_client)
    predictor = CatBoostShapPredictor()
    telegram = TelegramNotificationAdapter()
    gmail = GmailNotificationAdapter()

    tool1 = Tool1ExtraerFuentesUseCase(repo, scraper)
    tool2 = Tool2ConsultarBdUseCase(repo)
    tool3 = Tool3PredecirRiesgoUseCase(repo, predictor)
    tool4 = Tool4ExplicarRiesgoUseCase(repo, predictor)
    tool5 = Tool5RedactarInformeUseCase()
    tool6 = Tool6NotificarUseCase(repo, telegram_notifier=telegram, gmail_notifier=gmail)

    # 1. Herramienta 1: extraer_fuentes (Primera ejecución -> detecta cambios y pobla serie 2014-2024)
    res1_first = tool1.execute(mode="backfill", start_year=2014, end_year=2024)
    assert res1_first["portales_consultados"] == 6
    assert res1_first["hubo_publicaciones_nuevas"] is True
    assert res1_first["registros_distritales_integrados"] == 100 * 11  # 100 distritos x 11 años (2014-2024)

    # Segunda ejecución inmediata -> control de cargas por hash SHA-256 detecta que NO hubo cambios
    res1_second = tool1.execute(mode="weekly_watch", start_year=2014, end_year=2024)
    assert res1_second["hubo_publicaciones_nuevas"] is False

    # 2. Herramienta 2: consultar_bd
    res2 = tool2.execute(ubigeo="090206", anio_inicio=2014, anio_fin=2024)
    assert res2["total_distritos_catalogo"] == 100
    assert res2["total_registros_serie"] == 11

    # 3. Validación de Métricas del Motor CatBoost + SHAP (Meta AUC >= 0.90)
    all_records = repo.get_historical_series(anio_inicio=2014, anio_fin=2024)
    metrics = predictor.train_and_evaluate(all_records)
    assert metrics["metricas_globales"]["auc_roc"] >= 0.90
    assert metrics["metricas_globales"]["cumple_meta_auc_090"] is True

    # 4. Herramienta 3: predecir_riesgo
    res3 = tool3.execute(anio_corte=2024)
    assert res3["total_distritos_evaluados"] == 100
    assert res3["activar_canal_algedonico_s5"] is True
    critical_ubigeo = res3["distritos_criticos_s5"][0]["ubigeo"]

    # 5. Herramienta 4: explicar_riesgo (SHAP para S3*)
    res4 = tool4.execute(ubigeo=critical_ubigeo)
    assert res4["ubigeo"] == critical_ubigeo
    assert len(res4["contribuciones_shap_ordenadas"]) == 10

    # 6. Herramienta 5: redactar_informe (Síntesis S4 + Recomendaciones PEI 2020-2027)
    res5 = tool5.execute(district_context=res4)
    assert res5["cumplimiento_ley_29733"] == "VERIFICADO_SOLO_INDICADORES_AGREGADOS"
    informe = res5["informe"]
    assert "OEI.01" in informe["alineacion_estrategica"]["pei_gore_huancavelica_2020_2027"]

    # 7. Herramienta 6: notificar (Regla Fija 2 Algedónica S5 + Regla Fija 3 Aprobación Humana S3)
    res6 = tool6.execute_dispatch(report_payload=informe)
    assert res6["regla_fija_algedonica_activada_s5"] is True
    assert res6["canal_destino"] == "S5_ALGEDONICO"
    assert len(telegram.sent_messages) == 1
    assert len(gmail.sent_emails) == 1

    # Simular Aprobación Humana desde celular (vía Cloudflare Tunnel) para publicar en S3 Control
    alert_id = res6["id_alerta"]
    approval_res = tool6.resolve_human_approval(alert_id=alert_id, approved=True)
    assert approval_res["publicado_en_canal_control_s3"] is True

