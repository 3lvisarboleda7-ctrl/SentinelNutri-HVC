"""Pruebas unitarias del módulo axiológico de Francisco Parra Luna (PRVU e ISDH-HVC)."""

import csv
from pathlib import Path

from sentinelnutri.domain.rules.parra_luna_axiological import (
    EXCLUDED_PRVU_DIMENSIONS,
    PRVU_DIMENSIONS,
    DistrictAxiologicalScore,
    compute_parra_luna_scores,
    evaluate_axiological_governance_rule,
    summarize_parra_luna_panel,
)


def test_parra_luna_prvu_selection_and_isdh_hvc_bounds() -> None:
    assert PRVU_DIMENSIONS == ("S", "RM", "Se", "CO", "JD", "CN")
    assert len(EXCLUDED_PRVU_DIMENSIONS) == 4

    panel_path = Path("data/exports/panel_distrital_hvc_2014_2024.csv")
    gov_path = Path("data/exports/matriz_gobernanza_oei_ods_hvc.csv")
    assert panel_path.exists()

    with panel_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    s5_ubigeos = []
    if gov_path.exists():
        with gov_path.open(encoding="utf-8") as f:
            s5_ubigeos = [r["ubigeo"] for r in csv.DictReader(f) if r.get("canal_msv_destino") == "S5_ALGEDONICO"]

    scores = compute_parra_luna_scores(rows, reference_rows=rows)
    assert len(scores) == 1100
    for s in scores:
        assert 0.0 <= s.indice_bruto_Y_arit <= 1.0
        assert 0.0 <= s.indice_bruto_Y_geom <= 1.0
        assert 1.0 <= s.denominador_X_inejecucion <= 2.0
        assert 0.0 <= s.isdh_hvc_arit <= s.indice_bruto_Y_arit + 1e-9
        assert s.isdh_hvc_geom <= s.isdh_hvc_arit + 1e-6

    summary = summarize_parra_luna_panel(rows, s5_ubigeos=s5_ubigeos)
    prog = summary["progreso_longitudinal"]
    assert prog["anio_2024"]["ISDH_HVC_arit"] > prog["anio_2014"]["ISDH_HVC_arit"]
    assert prog["anio_2024"]["sigma_Y"] < prog["anio_2014"]["sigma_Y"]

    cmp_s5 = summary["comparativo_2024_s5_vs_s3"]
    assert cmp_s5["distritos_s5_algedonicos"]["n"] in (4, 5)
    assert cmp_s5["distritos_s5_algedonicos"]["ISDH_HVC_geom"] < cmp_s5["distritos_s3_control"]["ISDH_HVC_geom"]
    assert cmp_s5["distritos_s5_algedonicos"]["sigma_Y"] > cmp_s5["distritos_s3_control"]["sigma_Y"]
    assert summary["correlaciones_isdh_vs_dci"]["corte_2024_spearman_rho"] < -0.90

    fig5 = Path("docs/figures/fig5_perfil_axiologico_parra_luna_hvc.png")
    assert fig5.exists() and fig5.stat().st_size > 20_000

    # Validar también el endpoint REST GET /evaluation/parra_luna sobre SQLite temporal
    import tempfile
    from fastapi.testclient import TestClient
    from sentinelnutri.interfaces.api.main import create_app

    with tempfile.TemporaryDirectory(prefix="sentinelnutri_pl_", ignore_cleanup_errors=True) as tmp:
        app = create_app(database_url=f"sqlite:///{Path(tmp) / 'pl.db'}", raw_storage_dir=str(Path(tmp) / "raw"))
        client = TestClient(app)
        resp = client.get("/evaluation/parra_luna")
        assert resp.status_code == 200
        body = resp.json()
        assert body["progreso_longitudinal"]["anio_2024"]["ISDH_HVC_arit"] > body["progreso_longitudinal"]["anio_2014"]["ISDH_HVC_arit"]
        assert len(body["provincias_2024"]) == 7
        assert body["correlaciones_isdh_vs_dci"]["corte_2024_spearman_rho"] < -0.90


def test_axiological_governance_rules_and_audit_api() -> None:
    """
    Valida la Regla Fija 4 (Equilibrio Axiológico Parra Luna), la detección de espejismo asistencial
    y alerta pre-algedónica, la trazabilidad SHA-256 en Tool 6, el enriquecimiento axiológico de Tool 5
    y los nuevos endpoints REST `/evaluation/parra_luna/{ubigeo}` y `/governance/audit`.
    """
    import tempfile
    from fastapi.testclient import TestClient
    from sentinelnutri.application.tool_5_redactar_informe import Tool5RedactarInformeUseCase
    from sentinelnutri.application.tool_6_notificar import Tool6NotificarUseCase
    from sentinelnutri.infrastructure.persistence import (
        SqlAlchemyRepository,
        create_db_engine_and_session,
    )
    from sentinelnutri.interfaces.api.main import create_app

    panel_path = Path("data/exports/panel_distrital_hvc_2014_2024.csv")
    with panel_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    scores_2024 = {s.ubigeo: s for s in compute_parra_luna_scores(rows, reference_rows=rows) if s.anio == 2024}

    # 1. Santa Ana (090411): Desequilibrio Crítico + Espejismo Asistencial + Cuello de botella CN (OEI.10)
    dec_santa_ana = evaluate_axiological_governance_rule(scores_2024["090411"])
    assert dec_santa_ana.estado_equilibrio_axiologico == "DESEQUILIBRIO_CRITICO_AXIOLOGICO"
    assert dec_santa_ana.espejismo_asistencial_detectado is True
    assert dec_santa_ana.cuello_de_botella_prvu == "CN"
    assert "OEI.10" in dec_santa_ana.oei_prioritario
    assert dec_santa_ana.brecha_horizontalizacion > 0.80

    # 2. Nuevo Occoro (090114): Alerta temprana pre-algedónica (DCI <= 25% pero ISDH_geom < 45% + PAN < 75%)
    dec_occoro = evaluate_axiological_governance_rule(scores_2024["090114"])
    assert dec_occoro.estado_equilibrio_axiologico == "DESEQUILIBRIO_CRITICO_AXIOLOGICO"
    assert dec_occoro.alerta_temprana_pre_algedonica is True
    assert dec_occoro.alerta_inejecucion_pan is True

    # 3. Izcuchaca (090109): Perfil equilibrado sin espejismo asistencial
    dec_izcuchaca = evaluate_axiological_governance_rule(scores_2024["090109"])
    assert dec_izcuchaca.estado_equilibrio_axiologico == "EQUILIBRADO"
    assert dec_izcuchaca.espejismo_asistencial_detectado is False

    # 4. Rechazo defensivo de NaN en evaluate_axiological_governance_rule
    corrupt = DistrictAxiologicalScore(
        ubigeo="090101", anio=2024, provincia="Huancavelica", distrito="Test", red_salud="Red",
        tasa_dci_pct=20.0, ejecucion_pan_mef_pct=80.0,
        dim_S=float("nan"), dim_RM=0.5, dim_Se=0.5, dim_CO=0.5, dim_JD=0.5, dim_CN=0.5,
        indice_bruto_Y_arit=0.5, indice_bruto_Y_geom=0.5, desequilibrio_sigma_Y=0.1,
        denominador_X_inejecucion=1.2, isdh_hvc_arit=0.4, isdh_hvc_geom=0.4,
    )
    raised = False
    try:
        evaluate_axiological_governance_rule(corrupt)
    except ValueError:
        raised = True
    assert raised is True

    # 5. Tool 5 enriquecido con perfil axiológico + sanitización defensiva de salida LLM (Ley 29733)
    class LeakyOutputLLM:
        def generate_policy_report(self, safe_context, prefer_provider="gemini"):
            return {
                "sintesis_narrativa_s4": "Alerta para menor con DNI 44556677 en zona altoandina.",
                "recomendacion_salud": "Brigadas CRED DIRESA.",
                "recomendacion_agua_saneamiento": "Cloración ATM DRVCS.",
                "recomendacion_agricultura_midis": "Devengado PAN 0001.",
            }, "mock-llm"

    t5_leaky = Tool5RedactarInformeUseCase(llm_gateway=LeakyOutputLLM())
    rep_out = t5_leaky.execute(
        {
            "ubigeo": "090411",
            "provincia": "Castrovirreyna",
            "distrito": "Santa Ana",
            "dci_proyectada_pct": 29.29,
            "perfil_axiologico": dec_santa_ana.to_dict(),
        }
    )
    assert "44556677" not in rep_out["informe"]["sintesis_narrativa_s4"]
    assert "[DNI_PROTEGIDO_LEY_29733]" in rep_out["informe"]["sintesis_narrativa_s4"]
    assert rep_out["informe"]["diagnostico_axiologico_parra_luna"]["cuello_de_botella_prvu"] == "CN"

    # 6. Tool 6 huella SHA-256 + guardia de approver_name corto (<3 chars) + endpoints REST de auditoría
    with tempfile.TemporaryDirectory(prefix="sentinelnutri_gov_", ignore_cleanup_errors=True) as tmp:
        db_url = f"sqlite:///{Path(tmp) / 'gov.db'}"
        app = create_app(database_url=db_url, raw_storage_dir=str(Path(tmp) / "raw"))
        client = TestClient(app)

        # GET /evaluation/parra_luna/090411 (200) y validaciones 400/404
        r_dist = client.get("/evaluation/parra_luna/090411")
        assert r_dist.status_code == 200
        d_body = r_dist.json()
        assert d_body["regla_fija_4_equilibrio_axiologico"]["estado_equilibrio_axiologico"] == "DESEQUILIBRIO_CRITICO_AXIOLOGICO"
        assert d_body["regla_fija_4_equilibrio_axiologico"]["espejismo_asistencial_detectado"] is True
        assert d_body["delta_isdh_geom_2014_2024_pp"] is not None

        assert client.get("/evaluation/parra_luna/999999").status_code == 400
        assert client.get("/evaluation/parra_luna/099999").status_code == 404

        # Despacho Tool 6 -> verifica huella SHA-256 y resolución HITL
        r_notif = client.post("/tools/notificar", json={"report_payload": rep_out["informe"]})
        assert r_notif.status_code == 200
        n_body = r_notif.json()
        assert len(n_body["huella_auditoria_sha256"]) == 64

        r_short_approver = client.post(
            f"/hitl/aprobar/{n_body['id_alerta']}",
            json={"approved": True, "approver_name": "ok"},
        )
        assert r_short_approver.status_code == 422

        r_ok_approver = client.post(
            f"/hitl/aprobar/{n_body['id_alerta']}",
            json={"approved": True, "approver_name": "Directora GRDS Huancavelica"},
        )
        assert r_ok_approver.status_code == 200
        assert len(r_ok_approver.json()["huella_resolucion_sha256"]) == 64

        # GET /governance/audit consolidado + verificación de persistencia SHA-256 en BD
        r_audit = client.get("/governance/audit")
        assert r_audit.status_code == 200
        a_body = r_audit.json()
        assert a_body["cumplimiento_ley_29733"]["activo"] is True
        assert a_body["auditoria_alertas_msv"]["total_alertas_registradas"] == 1
        assert a_body["auditoria_alertas_msv"]["alertas_con_huella_sha256_persistida"] == 1
        assert a_body["auditoria_alertas_msv"]["resoluciones_con_huella_sha256_persistida"] == 1
        assert a_body["auditoria_alertas_msv"]["por_estado_hitl"]["APROBADO_S3"] == 1
        assert a_body["gobernanza_axiologica_2024"]["desequilibrio_critico"] >= 4
        assert a_body["gobernanza_axiologica_2024"]["espejismo_asistencial_count"] >= 4
        assert a_body["distritos_alerta_pre_algedonica"] >= 1

        # Verificar protección opcional por cabecera X-API-Key cuando SENTINEL_API_KEY está configurada
        import os

        old_key = os.environ.get("SENTINEL_API_KEY")
        try:
            os.environ["SENTINEL_API_KEY"] = "secret_gore_hvc_key_2026"
            r_unauth = client.post("/tools/notificar", json={"report_payload": rep_out["informe"]})
            assert r_unauth.status_code == 401
            r_auth = client.post(
                "/tools/notificar",
                json={"report_payload": rep_out["informe"]},
                headers={"X-API-Key": "secret_gore_hvc_key_2026"},
            )
            assert r_auth.status_code == 200
        finally:
            if old_key is None:
                os.environ.pop("SENTINEL_API_KEY", None)
            else:
                os.environ["SENTINEL_API_KEY"] = old_key
