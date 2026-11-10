"""
Suite de Pruebas Adversariales Red-Team & Chaos QA — SentinelNutri-HVC (Sistema 4 del MSV).

Valida el blindaje de las decisiones de las Fases 1 y 2 frente a ataques e entradas corruptas:
1. Ruptura 1 — Guardarraíl Ley N.° 29733 (`privacy_guard.py`): Estructuras profundamente anidadas
   (listas de listas, tuplas de dicts), variantes compuestas de nombres de campos (`DNI_Menor`,
   `num_historia_clinica`, `telefono_celular`, `Apellidos_Paciente`) y DNI infiltrado en texto libre.
2. Ruptura 2 — Las 3 Reglas Fijas y Motor Predictivo (`fixed_thresholds.py` y `catboost_shap_predictor.py`):
   Valores borde exactos (`25.0`, `25.0000001`, `24.9999999`, `0.0`), valores fuera de rango (`-5.0`, `150.0`),
   `float('nan')`, `float('inf')` y ubigeos malformados.
3. Ruptura 3 — Persistencia e Integridad Referencial (`database.py` y `postgres_repo.py`):
   Bloqueo de ubigeos huérfanos inexistentes (`999999`) por `FOREIGN KEY` activa y rendimiento de
   inserción/consulta sobre las 1 100 filas (100 distritos × 11 años).
"""

import math
import os
import sqlite3
import tempfile
import shutil
import time

from sentinelnutri.domain.entities.alert_msv import MSVChannel
from sentinelnutri.domain.entities.district import DistrictIndicatorRecord
from sentinelnutri.domain.entities.prediction import RiskLevel
from sentinelnutri.domain.rules.fixed_thresholds import (
    classify_risk_level,
    evaluate_fixed_algedonic_rule,
)
from sentinelnutri.domain.rules.privacy_guard import (
    PrivacyViolationError,
    sanitize_district_payload_for_llm,
)
from sentinelnutri.infrastructure.ml_xai.catboost_shap_predictor import CatBoostShapPredictor
from sentinelnutri.infrastructure.persistence.database import (
    DEFAULT_HUANCAVELICA_DISTRICTS,
    create_db_engine_and_session,
)
from sentinelnutri.infrastructure.persistence.postgres_repo import SqlAlchemyRepository


def _build_valid_record(ubigeo: str = "090101", tasa_dci_pct: float = 24.5) -> DistrictIndicatorRecord:
    return DistrictIndicatorRecord(
        ubigeo=ubigeo,
        anio=2024,
        semestre=2,
        tasa_dci_pct=tasa_dci_pct,
        tasa_anemia_pct=52.0,
        tasa_bajo_peso_pct=7.5,
        ninos_evaluados=310,
        pobreza_monetaria_pct=38.0,
        educacion_materna_secundaria_pct=58.0,
        agua_cloro_adecuado_pct=14.0,
        saneamiento_basico_pct=48.0,
        controles_cred_completo_pct=68.0,
        lactancia_materna_exclusiva_pct=74.0,
        ejecucion_pan_mef_pct=76.0,
        presupuesto_pan_per_capita_soles=420.0,
        cobertura_juntos_pct=72.0,
        cobertura_cuna_mas_pct=48.0,
        cobertura_qali_warma_pct=86.0,
        dias_heladas_anual=82,
        temp_minima_promedio_c=-1.5,
        precipitacion_anual_mm=680.0,
    )


def test_red_team_1_privacy_guard_nested_and_variant_keys() -> None:
    """
    Intento de Ruptura 1: Verifica que claves con variantes (`DNI_Menor`, `num_historia_clinica`,
    `telefono_celular`, `Apellidos`), estructuras anidadas (listas de listas y tuplas con dicts) y
    DNIs en texto libre sean bloqueados en modo estricto y limpiados en modo no estricto.
    """
    variant_vectors = [
        {"ubigeo": "090101", "DNI_Menor": "71234567"},
        {"ubigeo": "090101", "nombre_madre": "María Quispe"},
        {"ubigeo": "090101", "Apellidos": "Huamán Taipe"},
        {"ubigeo": "090101", "num_historia_clinica": "HC-2024-889"},
        {"ubigeo": "090101", "telefono_celular": "987654321"},
        {"ubigeo": "090101", "lotes_anidados": [[{"dni": "12345678", "tasa": 25.0}]]},
        {"ubigeo": "090101", "tupla_oculta": ({"apellido_paterno": "Condori"},)},
        {"ubigeo": "090101", "observacion_campo": "Atención realizada al menor con DNI: 45678901 en posta"},
    ]

    for vector in variant_vectors:
        blocked = False
        try:
            sanitize_district_payload_for_llm(vector, strict=True)
        except PrivacyViolationError:
            blocked = True
        assert blocked is True, f"El vector adversarial no fue bloqueado en strict=True: {vector}"

    # En modo strict=False debe limpiar recursivamente todas las claves y redactar el DNI en texto libre
    complex_payload = {
        "ubigeo": "090206",
        "nombre_distrito": "Paucará",  # Excepción segura permitida
        "dci_proyectada_pct": 28.4,
        "DNI_Menor": "71234567",
        "num_historia_clinica": "HC-0091",
        "telefono_celular": "999111222",
        "jerarquia_redes": [
            [
                {
                    "microred": "Paucará",
                    "nombre_madre": "Rosa",
                    "Apellidos": "Ccahuana",
                    "indicador_agregado": 29.1,
                }
            ]
        ],
        "tupla_auditoria": ({"dni_apoderado": "11223344", "valido": True},),
        "nota_resumen": "Caso reportado con DNI 87654321 en centro poblado",
    }
    cleaned = sanitize_district_payload_for_llm(complex_payload, strict=False)
    assert cleaned["ubigeo"] == "090206"
    assert cleaned["nombre_distrito"] == "Paucará"
    assert "DNI_Menor" not in cleaned
    assert "num_historia_clinica" not in cleaned
    assert "telefono_celular" not in cleaned
    inner_dict = cleaned["jerarquia_redes"][0][0]
    assert "nombre_madre" not in inner_dict
    assert "Apellidos" not in inner_dict
    assert inner_dict["indicador_agregado"] == 29.1
    assert "dni_apoderado" not in cleaned["tupla_auditoria"][0]
    assert "87654321" not in cleaned["nota_resumen"]
    assert "[DNI_PROTEGIDO_LEY_29733]" in cleaned["nota_resumen"]


def test_red_team_2_boundary_and_corrupted_values_in_rules_and_predictor() -> None:
    """
    Intento de Ruptura 2: Prueba límites exactos (25.0, 25.0000001, 24.9999999, 0.0)
    y verifica el rechazo defensivo de NaN, Inf, valores negativos (-5.0) o >100% (150.0).
    """
    # 1. Límites exactos alrededor de 25.0%
    dec_exact_25 = evaluate_fixed_algedonic_rule("090101", 25.0)
    assert dec_exact_25.supera_umbral_critico is False
    assert dec_exact_25.canal_obligatorio == MSVChannel.S3_CONTROL
    assert classify_risk_level(25.0) == RiskLevel.ALTO

    dec_just_above = evaluate_fixed_algedonic_rule("090101", 25.0000001)
    assert dec_just_above.supera_umbral_critico is True
    assert dec_just_above.canal_obligatorio == MSVChannel.S5_ALGEDONICO
    assert classify_risk_level(25.0000001) == RiskLevel.CRITICO

    dec_just_below = evaluate_fixed_algedonic_rule("090101", 24.9999999)
    assert dec_just_below.supera_umbral_critico is False
    assert dec_just_below.canal_obligatorio == MSVChannel.S3_CONTROL
    assert classify_risk_level(24.9999999) == RiskLevel.ALTO

    dec_zero = evaluate_fixed_algedonic_rule("090101", 0.0)
    assert dec_zero.supera_umbral_critico is False
    assert classify_risk_level(0.0) == RiskLevel.BAJO

    # 2. Valores corruptos o fuera de dominio físico (-5.0, 150.0, NaN, Inf, -Inf)
    corrupted_values = [-5.0, 150.0, float("nan"), float("inf"), float("-inf")]
    for bad_val in corrupted_values:
        raised_rule = False
        try:
            evaluate_fixed_algedonic_rule("090101", bad_val)
        except ValueError:
            raised_rule = True
        assert raised_rule is True, f"evaluate_fixed_algedonic_rule no rechazó el valor inválido: {bad_val}"

        raised_class = False
        try:
            classify_risk_level(bad_val)
        except ValueError:
            raised_class = True
        assert raised_class is True, f"classify_risk_level no rechazó el valor inválido: {bad_val}"

    # 3. Validación defensiva en CatBoostShapPredictor ante NaN, Inf o porcentajes fuera de rango
    predictor = CatBoostShapPredictor()
    for bad_val in corrupted_values:
        bad_record = _build_valid_record(ubigeo="090101", tasa_dci_pct=bad_val)
        raised_pred = False
        try:
            predictor.predict_district_risk(bad_record)
        except ValueError:
            raised_pred = True
        assert raised_pred is True, f"CatBoostShapPredictor no rechazó tasa_dci_pct={bad_val}"


def test_red_team_3_persistence_referential_integrity_and_1100_rows_performance() -> None:
    """
    Intento de Ruptura 3: Verifica que la base de datos rechace ubigeos inexistentes (integridad
    referencial FOREIGN KEY activa) y procese las 1 100 filas (100 distritos × 11 años) con alta velocidad.
    """
    tmp_dir = tempfile.mkdtemp(prefix="sentinelnutri_redteam_")
    try:
        db_url = "sqlite:///" + os.path.join(tmp_dir, "redteam_test.db")
        _, conn_factory = create_db_engine_and_session(db_url)
        repo = SqlAlchemyRepository(conn_factory)

        # 1. Intento de insertar un ubigeo inexistente fuera de Huancavelica ('999999')
        orphan_record = _build_valid_record(ubigeo="999999", tasa_dci_pct=26.0)
        fk_blocked = False
        try:
            repo.upsert_historical_records([orphan_record])
        except sqlite3.IntegrityError:
            fk_blocked = True
        assert fk_blocked is True, "SQLite permitió insertar un ubigeo huérfano ('999999') sin FOREIGN KEY!"

        # 2. Inserción y consulta de las 1 100 filas (100 distritos × 11 años: 2014-2024)
        panel_1100 = [
            _build_valid_record(ubigeo=d.ubigeo, tasa_dci_pct=22.0 + (anio - 2014) * 0.3)
            for d in DEFAULT_HUANCAVELICA_DISTRICTS
            for anio in range(2014, 2025)
        ]
        # Ajustar el año de cada registro en la comprensión
        for idx, rec in enumerate(panel_1100):
            rec.anio = 2014 + (idx % 11)

        t0 = time.perf_counter()
        inserted = repo.upsert_historical_records(panel_1100)
        upsert_ms = (time.perf_counter() - t0) * 1000.0
        assert inserted == 1100

        t1 = time.perf_counter()
        fetched = repo.get_historical_series(anio_inicio=2014, anio_fin=2024)
        query_ms = (time.perf_counter() - t1) * 1000.0
        assert len(fetched) == 1100
        assert upsert_ms < 1000.0, f"Upsert de 1100 filas demasiado lento: {upsert_ms:.2f} ms"
        assert query_ms < 500.0, f"Consulta de 1100 filas demasiado lenta: {query_ms:.2f} ms"
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_red_team_4_fastapi_endpoints_and_hitl_security() -> None:
    """
    Intento de Ruptura 4 (Fases 3, 4 y 5): Prueba mediante TestClient de FastAPI inyecciones SQL y
    ubigeos inexistentes en `/tools/explicar_riesgo/{ubigeo}` y `/predict`, payloads corruptos o con
    datos nominales en `/tools/redactar_informe` y `/tools/notificar`, y aprobación HITL inexistente
    en `/hitl/aprobar/999999`, verificando códigos HTTP semánticos (400/404/422) y cero errores 500.
    """
    from fastapi.testclient import TestClient
    from sentinelnutri.interfaces.api.main import create_app

    tmp_dir = tempfile.mkdtemp(prefix="sentinelnutri_api_rt_")
    try:
        db_url = "sqlite:///" + os.path.join(tmp_dir, "api_redteam.db")
        raw_dir = os.path.join(tmp_dir, "raw")
        app = create_app(database_url=db_url, raw_storage_dir=raw_dir)
        client = TestClient(app, raise_server_exceptions=False)

        # 1. Inyección SQL / Ubigeo malformado en /tools/explicar_riesgo/{ubigeo} -> 400 Bad Request (sin DoS backfill)
        r_sqli = client.get("/tools/explicar_riesgo/090101'%20OR%20'1'='1")
        assert r_sqli.status_code == 400, f"Esperado 400 ante SQLi, recibido: {r_sqli.status_code}"

        # 2. Ubigeo de 6 dígitos fuera de Huancavelica ('999999') o inexistente ('099999') -> 400 / 404
        r_out_dept = client.get("/tools/explicar_riesgo/999999")
        assert r_out_dept.status_code == 400
        r_non_existent_hvc = client.get("/tools/explicar_riesgo/099999")
        assert r_non_existent_hvc.status_code == 404

        # 3. /predict con ubigeo inexistente o inyección -> 400 / 404
        r_pred_sqli = client.post("/predict", json={"ubigeo": "090101' DROP TABLE", "anio_corte": 2024})
        assert r_pred_sqli.status_code == 400
        r_pred_404 = client.post("/predict", json={"ubigeo": "099999", "anio_corte": 2024})
        assert r_pred_404.status_code == 404

        # 4. /tools/redactar_informe con violación Ley 29733 o DCI fuera de rango (-15.0%) -> 422 (nunca 500)
        r_pii = client.post(
            "/tools/redactar_informe",
            json={"district_context": {"ubigeo": "090101", "DNI_Menor": "71234567", "dci_proyectada_pct": 26.0}},
        )
        assert r_pii.status_code == 422

        r_neg_dci = client.post(
            "/tools/redactar_informe",
            json={"district_context": {"ubigeo": "090101", "dci_proyectada_pct": -15.0}},
        )
        assert r_neg_dci.status_code == 422

        # 5. /tools/notificar con ubigeo huérfano ('999999') o DCI corrupta (180.0%) -> 400 / 422 (nunca 500)
        r_notif_orphan = client.post(
            "/tools/notificar",
            json={"report_payload": {"ubigeo": "999999", "dci_proyectada_pct": 28.0}},
        )
        assert r_notif_orphan.status_code in (400, 404)

        r_notif_bad_dci = client.post(
            "/tools/notificar",
            json={"report_payload": {"ubigeo": "090101", "dci_proyectada_pct": 180.0}},
        )
        assert r_notif_bad_dci.status_code == 422

        # 6. Aprobación HITL de alerta inexistente (/hitl/aprobar/999999) -> 404 Not Found
        r_hitl_404 = client.post("/hitl/aprobar/999999", json={"approved": True})
        assert r_hitl_404.status_code == 404
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_red_team_5_llm_gateway_3_tier_failover_and_truncated_json() -> None:
    """
    Intento de Ruptura 5: Verifica la conmutación por fallo (Failover) entre las 3 rutas del LLM Gateway:
    Ruta A (Gemini API) -> Ruta B (Ollama GTX 1050) -> Ruta C (Respaldo determinista estructurado MSV),
    simulando respuestas JSON truncadas o caídas de red y garantizando que jamás se bloquee el Canal Algedónico S5.
    """
    from sentinelnutri.application.tool_5_redactar_informe import Tool5RedactarInformeUseCase
    from sentinelnutri.infrastructure.notifications.llm_gateway import (
        AgnosticLLMGateway,
        is_valid_llm_policy_response,
    )

    # 1. Validación estricta del contrato JSON de 4 claves obligatorias
    assert is_valid_llm_policy_response({"sintesis_narrativa_s4": "Solo una clave"}) is False
    assert is_valid_llm_policy_response(
        {
            "sintesis_narrativa_s4": "Síntesis S4",
            "recomendacion_salud": "Salud DIRESA",
            "recomendacion_agua_saneamiento": "Agua DRVCS",
            "recomendacion_agricultura_midis": "Agro DRA/MIDIS",
        }
    ) is True

    # 2. Simulación de Ruta A caída -> Failover automático a Ruta B (Ollama GTX 1050)
    class FailoverToOllamaGateway(AgnosticLLMGateway):
        def _try_gemini(self, payload):
            return None  # Simula timeout o cuota agotada en Gemini

        def _try_ollama(self, payload):
            return {
                "sintesis_narrativa_s4": "[Ollama GTX 1050] Diagnóstico local S4.",
                "recomendacion_salud": "Brigadas CRED DIRESA.",
                "recomendacion_agua_saneamiento": "Cloración ATM DRVCS.",
                "recomendacion_agricultura_midis": "Devengado PAN 0001 y Juntos.",
            }

    gw_b = FailoverToOllamaGateway(gemini_api_key="AIza_fake_key_for_test")
    res_b, provider_b = gw_b.generate_policy_report({"ubigeo": "090411", "dci_proyectada_pct": 29.5}, prefer_provider="gemini")
    assert res_b is not None
    assert "ollama/llama3.2" in provider_b

    # 3. Simulación de JSON truncado/corrupto desde un LLM -> Recuperación automática por Ruta C sin bloquear S5
    class TruncatedJSONGateway:
        def generate_policy_report(self, safe_context, prefer_provider="gemini"):
            # Devuelve un dict incompleto (falta recomendacion_salud, etc.)
            return {"sintesis_narrativa_s4": "JSON truncado a mitad de red..."}, "broken-llm"

    tool5 = Tool5RedactarInformeUseCase(llm_gateway=TruncatedJSONGateway())
    out = tool5.execute({"ubigeo": "090411", "provincia": "Castrovirreyna", "distrito": "Santa Ana", "dci_proyectada_pct": 29.5})
    assert out["informe"]["canal_destino"] == "S5_ALGEDONICO"
    assert "DIRESA" in out["informe"]["recomendaciones_sectoriales"]["salud_diresa"]
    assert "fallback-determinista-msv" in out["proveedor_llm_utilizado"]


def test_red_team_6_n8n_workflows_structural_and_rules_audit() -> None:
    """
    Intento de Ruptura 6: Audita programáticamente los JSON de `workflows_n8n/01_ciclo_supervisor_sentinelnutri.json`
    y `02_vigilancia_fallos_scrapers.json`, verificando que todos los nodos, conexiones, umbral fijo (25.0)
    y webhook HITL (`/hitl/aprobar`) estén íntegros y conectados sin nodos huérfanos.
    """
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    w1_path = root / "workflows_n8n" / "01_ciclo_supervisor_sentinelnutri.json"
    w2_path = root / "workflows_n8n" / "02_vigilancia_fallos_scrapers.json"

    w1 = json.loads(w1_path.read_text(encoding="utf-8"))
    w2 = json.loads(w2_path.read_text(encoding="utf-8"))

    # 1. Auditoría de 01_ciclo_supervisor_sentinelnutri.json
    nodes_w1 = {n["name"]: n for n in w1["nodes"]}
    assert len(nodes_w1) >= 14
    conns_w1 = w1["connections"]
    assert len(conns_w1) >= 11, "El grafo de conexiones del workflow 01 de n8n está incompleto."

    # Verificar que todos los nodos referenciados en connections existan en `nodes`
    for src_name, branches in conns_w1.items():
        assert src_name in nodes_w1, f"Nodo origen inexistente en connections: {src_name}"
        for conn_type, groups in branches.items():
            for group in groups:
                for edge in group:
                    assert edge["node"] in nodes_w1, f"Nodo destino inexistente en connections: {edge['node']}"

    # Verificar el Nodo IF de la Regla Fija 2 (DCI proyectada > 25.0)
    if_node = nodes_w1["Regla Fija 2: Nodo IF · Umbral de Riesgo (DCI proyectada > 25% -> S5)"]
    num_cond = if_node["parameters"]["conditions"]["number"][0]
    assert num_cond["operation"] == "larger"
    assert float(num_cond["value2"]) == 25.0

    # Verificar el nodo de callback HITL (/hitl/aprobar/{alert_id})
    hitl_cb = nodes_w1["Confirmar Aprobación HITL hacia S3 (/hitl/aprobar/{alert_id})"]
    assert "/hitl/aprobar/" in hitl_cb["parameters"]["url"]

    # 2. Auditoría de 02_vigilancia_fallos_scrapers.json
    nodes_w2 = {n["name"]: n for n in w2["nodes"]}
    assert len(nodes_w2) == 2
    conns_w2 = w2["connections"]
    assert "Error Trigger (Fallo en Scraper por Cambio de Diseño de Portal)" in conns_w2


def test_red_team_7_dashboard_4_rooms_and_hitl_approver_guard() -> None:
    """
    Intento de Ruptura 7 (Fase 5 — Dashboard Streamlit y HITL):
    1. Verifica que al inicializar el Dashboard sobre una BD donde `serie_historica_distrital` tiene datos
       pero `predicciones_dci` está vacía, `init_services` y `build_dashboard_rooms_snapshot` autopueblen
       las 100 predicciones sin lanzar `KeyError(None)` en la Sala 2 (S3* SHAP).
    2. Verifica que la caché de evaluación reduzca drásticamente el tiempo de re-renderizado de la Sala 4.
    3. Verifica que `Tool6NotificarUseCase.resolve_human_approval` rechace nombres de aprobador vacíos
       (`""` o `"   "`) garantizando trazabilidad nominal de la autoridad S3 (GRDS).
    """
    from sentinelnutri.application.tool_1_extraer_fuentes import Tool1ExtraerFuentesUseCase
    from sentinelnutri.application.tool_6_notificar import Tool6NotificarUseCase
    from sentinelnutri. infrastructure.scrapers import MultiSourceScraperOrchestrator
    from sentinelnutri.interfaces.dashboard.app import (
        build_dashboard_rooms_snapshot,
        init_services,
    )

    tmp_dir = tempfile.mkdtemp(prefix="sentinelnutri_dash_rt_")
    try:
        db_url = "sqlite:///" + os.path.join(tmp_dir, "dash_redteam.db")
        _, sf = create_db_engine_and_session(db_url)
        repo = SqlAlchemyRepository(sf)
        scraper = MultiSourceScraperOrchestrator(repository=repo)
        tool1 = Tool1ExtraerFuentesUseCase(repo, scraper)

        # Simular el caso borde: Serie histórica poblada (1 100 filas), pero 0 predicciones en `predicciones_dci`
        tool1.execute(mode="backfill", start_year=2014, end_year=2024, force_rebuild=True)
        assert len(repo.get_latest_predictions()) == 0

        # `build_dashboard_rooms_snapshot` debe autopoblar las 100 predicciones y construir las 4 salas sin KeyError
        t0 = time.perf_counter()
        snap1 = build_dashboard_rooms_snapshot(db_url)
        t_first_ms = (time.perf_counter() - t0) * 1000.0

        t1 = time.perf_counter()
        snap2 = build_dashboard_rooms_snapshot(db_url)
        t_cached_ms = (time.perf_counter() - t1) * 1000.0

        assert snap1["sala_1_homeostato_count"] == 100
        assert snap1["sala_1_criticos_s5_count"] > 0
        assert snap1["sala_2_shap_options_count"] == 100
        assert len(snap1["sala_2_sample_explanation"]["contribuciones_shap_ordenadas"]) == 10
        assert snap1["sala_4_metrics_globales"]["auc_roc"] >= 0.90
        assert t_cached_ms < t_first_ms, "La caché de métricas del Dashboard debería acelerar el segundo render."

        # Verificar bloqueo de aprobación HITL sin nombre de autoridad responsable (approver_name en blanco)
        tool6 = Tool6NotificarUseCase(repo)
        dispatch_res = tool6.execute_dispatch(
            {"ubigeo": "090101", "provincia": "Huancavelica", "distrito": "Huancavelica", "dci_proyectada_pct": 19.5}
        )
        alert_id = dispatch_res["id_alerta"]

        for blank_name in ("", "   "):
            rejected = False
            try:
                tool6.resolve_human_approval(alert_id=alert_id, approved=True, approver_name=blank_name)
            except ValueError:
                rejected = True
            assert rejected is True, f"Debió rechazar approver_name vacío: {blank_name!r}"
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_red_team_8_exported_artifacts_and_figures_integrity() -> None:
    """
    Intento de Ruptura 8: Audita programáticamente la integridad de los artefactos exportados en
    `data/exports/` y `docs/figures/`:
    - `panel_distrital_hvc_2014_2024.csv`: Exactamente 1 100 filas, 100 distritos únicos y 0 valores nulos/NaN.
    - `matriz_gobernanza_oei_ods_hvc.csv`: Exactamente 100 distritos, canales `S5_ALGEDONICO` y `S3_CONTROL`
      consistentes con `dci_proyectada_pct > 25.0`, y alineación a OEI del PEI 2020-2027 y ODS 2, 3 y 6.
    - `metrics_report.json`: `auc_roc >= 0.90` y cobertura de las 7 provincias en `resumen_por_provincia_s2`.
    - Existencia y tamaño no nulo de las 4 figuras PNG de 300 DPI en `docs/figures/`.
    """
    import csv
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    panel_csv = root / "data" / "exports" / "panel_distrital_hvc_2014_2024.csv"
    gov_csv = root / "data" / "exports" / "matriz_gobernanza_oei_ods_hvc.csv"
    metrics_json = root / "data" / "exports" / "metrics_report.json"

    assert panel_csv.exists(), "Falta panel_distrital_hvc_2014_2024.csv"
    assert gov_csv.exists(), "Falta matriz_gobernanza_oei_ods_hvc.csv"
    assert metrics_json.exists(), "Falta metrics_report.json"

    with panel_csv.open("r", encoding="utf-8") as f:
        panel_rows = list(csv.DictReader(f))
    assert len(panel_rows) == 1100, f"Se esperaban 1100 filas en el panel, se encontraron {len(panel_rows)}"
    distinct_ubigeos = {r["ubigeo"] for r in panel_rows}
    assert len(distinct_ubigeos) == 100
    for row in panel_rows:
        for k, v in row.items():
            assert v is not None and str(v).strip() != "" and str(v).lower() != "nan", f"Valor nulo/NaN en {k}"

    with gov_csv.open("r", encoding="utf-8") as f:
        gov_rows = list(csv.DictReader(f))
    assert len(gov_rows) == 100, f"Se esperaban 100 distritos en matriz de gobernanza, hay {len(gov_rows)}"
    for r in gov_rows:
        dci_proj = float(r["dci_proyectada_pct"])
        expected_channel = "S5_ALGEDONICO" if dci_proj > 25.0 else "S3_CONTROL"
        assert r["canal_msv_destino"] == expected_channel
        assert "OEI.01" in r["oei_pei_vinculados"]
        assert "ODS 2" in r["ods_vinculados"]

    metrics = json.loads(metrics_json.read_text(encoding="utf-8"))
    assert float(metrics["metricas_globales"]["auc_roc"]) >= 0.90
    assert metrics["metricas_globales"]["cumple_meta_auc_090"] is True
    assert len(metrics["resumen_por_provincia_s2"]) == 7

    expected_figs = [
        "fig1_roc_cv5_catboost_hvc.png",
        "fig2_shap_importancia_global_s3_star.png",
        "fig3_shap_waterfall_distrito_critico.png",
        "fig4_homeostato_s3_s4_7_provincias.png",
    ]
    for fig_name in expected_figs:
        fig_path = root / "docs" / "figures" / fig_name
        assert fig_path.exists() and fig_path.stat().st_size > 10_000, f"Figura inválida o vacía: {fig_name}"


