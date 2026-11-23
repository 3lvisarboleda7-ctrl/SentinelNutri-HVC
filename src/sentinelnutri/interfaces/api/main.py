"""
Aplicación Principal FastAPI — SentinelNutri-HVC (Microservicio de Herramientas S4 y Motor Predictivo).

Expone los contratos REST exactos consumidos por el Agente Supervisor de n8n (Tabla 5 del Proyecto)
y por los recuadros de Reglas Fijas (Figura 1):
1. POST /tools/extraer_fuentes
2. GET  /tools/consultar_bd
3. POST /predict  (y alias POST /tools/predecir_riesgo)
4. GET  /tools/explicar_riesgo/{ubigeo}
5. POST /tools/redactar_informe
6. POST /tools/notificar
7. POST /hitl/aprobar/{alert_id} (Webhook de Aprobación Humana vía Cloudflare Tunnel)
8. GET  /evaluation/metrics      (Validación Cruzada Estratificada: AUC >= 0.90, F1, SHAP global)
"""

import os
import secrets
import sqlite3
from dataclasses import asdict
from typing import Any, Dict, Optional
from fastapi import Body, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field

from sentinelnutri.application import (
    Tool1ExtraerFuentesUseCase,
    Tool2ConsultarBdUseCase,
    Tool3PredecirRiesgoUseCase,
    Tool4ExplicarRiesgoUseCase,
    Tool5RedactarInformeUseCase,
    Tool6NotificarUseCase,
)
from sentinelnutri.domain.rules.fixed_thresholds import ALGEDONIC_DCI_THRESHOLD_PCT
from sentinelnutri.domain.rules.parra_luna_axiological import (
    compute_parra_luna_scores,
    evaluate_axiological_governance_rule,
    summarize_parra_luna_panel,
)
from sentinelnutri.domain.rules.privacy_guard import PrivacyViolationError
from sentinelnutri.infrastructure.ml_xai import CatBoostShapPredictor
from sentinelnutri.infrastructure.notifications import (
    AgnosticLLMGateway,
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


class ExtraerFuentesRequest(BaseModel):
    mode: str = Field(default="weekly_watch", description="'backfill' (2014-2024) o 'weekly_watch'")
    start_year: int = Field(default=2014, ge=2000, le=2030)
    end_year: int = Field(default=2024, ge=2000, le=2030)
    force_rebuild: bool = Field(default=False)


class PredictRequest(BaseModel):
    ubigeo: Optional[str] = Field(default=None, description="Ubigeo distrital (ej. '090101') o None para todos")
    anio_corte: int = Field(default=2024, ge=2014, le=2030)


class RedactarInformeRequest(BaseModel):
    district_context: Dict[str, Any] = Field(
        ..., description="Indicadores agregados del distrito y valores SHAP (sin datos nominales Ley 29733)"
    )
    prefer_provider: str = Field(default="gemini", description="'gemini' (Google AI Studio) u 'ollama' (GTX 1050)")


class NotificarRequest(BaseModel):
    report_payload: Dict[str, Any] = Field(..., description="Informe generado para enrutar hacia S3 o S5")


class HumanApprovalRequest(BaseModel):
    approved: bool = Field(..., description="True para aprobar publicación en Canal de Control S3")
    approver_name: str = Field(default="Responsable GRDS-S3 (Aprobado desde Celular vía Cloudflare Tunnel)")


def create_app(database_url: Optional[str] = None, raw_storage_dir: Optional[str] = None) -> FastAPI:
    """Factoría de la aplicación FastAPI con inyección limpia de dependencias."""
    _, session_factory = create_db_engine_and_session(database_url)
    repo = SqlAlchemyRepository(session_factory)
    scraper_client = EthicalWebScraperClient(raw_storage_dir=raw_storage_dir)
    scraper_orchestrator = MultiSourceScraperOrchestrator(repository=repo, scraper_client=scraper_client)
    predictor = CatBoostShapPredictor()
    llm_gateway = AgnosticLLMGateway()
    telegram_adapter = TelegramNotificationAdapter()
    gmail_adapter = GmailNotificationAdapter()

    tool1 = Tool1ExtraerFuentesUseCase(repository=repo, scraper_orchestrator=scraper_orchestrator)
    tool2 = Tool2ConsultarBdUseCase(repository=repo)
    tool3 = Tool3PredecirRiesgoUseCase(repository=repo, predictor=predictor)
    tool4 = Tool4ExplicarRiesgoUseCase(repository=repo, predictor=predictor)
    tool5 = Tool5RedactarInformeUseCase(llm_gateway=llm_gateway)
    tool6 = Tool6NotificarUseCase(
        repository=repo,
        telegram_notifier=telegram_adapter,
        gmail_notifier=gmail_adapter,
    )

    api = FastAPI(
        title="SentinelNutri-HVC API (Sistema 4 del MSV - GORE Huancavelica)",
        description=(
            "Microservicio de Costo Cero que expone el Motor Predictivo CatBoost+SHAP (/predict) "
            "y las 6 herramientas del Agente Supervisor en n8n bajo las 3 Reglas Fijas Cibernéticas."
        ),
        version="1.0.0",
    )

    # Guardar referencias en state para inspección en tests y dashboard
    api.state.repo = repo
    api.state.telegram = telegram_adapter
    api.state.gmail = gmail_adapter

    def _validate_ubigeo_or_raise(ubigeo: str) -> str:
        clean = str(ubigeo).strip()
        if len(clean) != 6 or not clean.isdigit() or not clean.startswith("09"):
            raise HTTPException(
                status_code=400,
                detail=f"Ubigeo malformado o inválido '{ubigeo}': debe ser un código de 6 dígitos de Huancavelica (09xxxx).",
            )
        valid_ubigeos = {d.ubigeo for d in repo.get_all_districts()}
        if clean not in valid_ubigeos:
            raise HTTPException(
                status_code=404,
                detail=f"El ubigeo '{clean}' no existe en el catálogo oficial de los 100 distritos de Huancavelica.",
            )
        return clean

    def _verify_api_key_if_configured(x_api_key: Optional[str]) -> None:
        expected = os.getenv("SENTINEL_API_KEY", "").strip()
        if not expected:
            return
        provided = (x_api_key or "").strip()
        if not provided or not secrets.compare_digest(provided, expected):
            raise HTTPException(
                status_code=401,
                detail="Acceso no autorizado: cabecera X-API-Key ausente o inválida.",
            )

    @api.get("/health", tags=["Infraestructura"])
    def health_check() -> Dict[str, object]:
        districts = repo.get_all_districts()
        return {
            "status": "OK",
            "sistema": "SentinelNutri-HVC (Sistema 4 del MSV - GORE Huancavelica)",
            "distritos_monitoreados": len(districts),
            "umbral_algedonico_fijo_pct": 25.0,
            "cumplimiento_ley_29733": True,
            "api_key_protection_enabled": bool(os.getenv("SENTINEL_API_KEY", "").strip()),
        }

    @api.post("/tools/extraer_fuentes", tags=["Herramientas del Agente Supervisor (Tabla 5)"])
    def endpoint_tool_1_extraer_fuentes(
        req: ExtraerFuentesRequest = Body(default_factory=ExtraerFuentesRequest),
        x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    ) -> Dict[str, object]:
        _verify_api_key_if_configured(x_api_key)
        return tool1.execute(
            mode=req.mode,
            start_year=req.start_year,
            end_year=req.end_year,
            force_rebuild=req.force_rebuild,
        )

    @api.get("/tools/consultar_bd", tags=["Herramientas del Agente Supervisor (Tabla 5)"])
    def endpoint_tool_2_consultar_bd(
        ubigeo: Optional[str] = Query(default=None),
        anio_inicio: int = Query(default=2014),
        anio_fin: int = Query(default=2024),
    ) -> Dict[str, object]:
        clean_ubigeo = _validate_ubigeo_or_raise(ubigeo) if ubigeo is not None else None
        return tool2.execute(ubigeo=clean_ubigeo, anio_inicio=anio_inicio, anio_fin=anio_fin)

    @api.post("/predict", tags=["Motor Predictivo CatBoost + SHAP y Herramienta 3"])
    @api.post("/tools/predecir_riesgo", tags=["Herramientas del Agente Supervisor (Tabla 5)"])
    def endpoint_tool_3_predecir_riesgo(
        req: PredictRequest = Body(default_factory=PredictRequest),
    ) -> Dict[str, object]:
        clean_ubigeo = _validate_ubigeo_or_raise(req.ubigeo) if req.ubigeo is not None else None
        # Si la base de datos aún está vacía, ejecuta automáticamente el backfill inicial 2014-2024
        if not repo.get_historical_series(anio_inicio=2014, anio_fin=2025):
            tool1.execute(mode="backfill", start_year=2014, end_year=2024, force_rebuild=True)
        try:
            return tool3.execute(ubigeo=clean_ubigeo, anio_corte=req.anio_corte)
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @api.get("/tools/explicar_riesgo/{ubigeo}", tags=["Herramientas del Agente Supervisor (Tabla 5)"])
    def endpoint_tool_4_explicar_riesgo(ubigeo: str) -> Dict[str, object]:
        clean_ubigeo = _validate_ubigeo_or_raise(ubigeo)
        if not repo.get_historical_series(ubigeo=clean_ubigeo, anio_inicio=2014, anio_fin=2025):
            tool1.execute(mode="backfill", start_year=2014, end_year=2024, force_rebuild=True)
        try:
            return tool4.execute(ubigeo=clean_ubigeo)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @api.post("/tools/redactar_informe", tags=["Herramientas del Agente Supervisor (Tabla 5)"])
    def endpoint_tool_5_redactar_informe(req: RedactarInformeRequest) -> Dict[str, Any]:
        try:
            if "ubigeo" in req.district_context and req.district_context["ubigeo"] is not None:
                _validate_ubigeo_or_raise(str(req.district_context["ubigeo"]))
            return tool5.execute(district_context=req.district_context, prefer_provider=req.prefer_provider)
        except PrivacyViolationError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except HTTPException:
            raise
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @api.post("/tools/notificar", tags=["Herramientas del Agente Supervisor (Tabla 5)"])
    def endpoint_tool_6_notificar(
        req: NotificarRequest,
        x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    ) -> Dict[str, Any]:
        _verify_api_key_if_configured(x_api_key)
        try:
            raw_ubigeo = req.report_payload.get("ubigeo", "090101")
            _validate_ubigeo_or_raise(str(raw_ubigeo))
            return tool6.execute_dispatch(report_payload=req.report_payload)
        except HTTPException:
            raise
        except (ValueError, TypeError, sqlite3.IntegrityError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @api.post("/hitl/aprobar/{alert_id}", tags=["Regla Fija 3: Aprobación Humana (HITL)"])
    def endpoint_human_approval(
        alert_id: int,
        req: HumanApprovalRequest,
        x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    ) -> Dict[str, Any]:
        _verify_api_key_if_configured(x_api_key)
        try:
            return tool6.resolve_human_approval(
                alert_id=alert_id,
                approved=req.approved,
                approver_name=req.approver_name,
            )
        except ValueError as exc:
            status_code = 422 if "approver_name" in str(exc) else 404
            raise HTTPException(status_code=status_code, detail=str(exc)) from exc

    @api.get("/evaluation/metrics", tags=["Semana 7: Evaluación y Gobernanza (AUC, F1, SHAP)"])
    def endpoint_evaluation_metrics() -> Dict[str, object]:
        records = repo.get_historical_series(anio_inicio=2014, anio_fin=2024)
        if not records:
            tool1.execute(mode="backfill", start_year=2014, end_year=2024, force_rebuild=True)
            records = repo.get_historical_series(anio_inicio=2014, anio_fin=2024)
        return predictor.train_and_evaluate(records)

    @api.get("/evaluation/parra_luna", tags=["Semana 7: Evaluación y Gobernanza (AUC, F1, SHAP)"])
    def endpoint_evaluation_parra_luna(
        include_all_districts: bool = Query(
            default=False,
            description="Si es True, incluye el vector completo de los 100 distritos en corte 2024",
        ),
    ) -> Dict[str, Any]:
        records = repo.get_historical_series(anio_inicio=2014, anio_fin=2024)
        if not records:
            tool1.execute(mode="backfill", start_year=2014, end_year=2024, force_rebuild=True)
            records = repo.get_historical_series(anio_inicio=2014, anio_fin=2024)
        preds = repo.get_latest_predictions()
        if not preds:
            tool3.execute(anio_corte=2024)
            preds = repo.get_latest_predictions()
        s5_ubigeos = [p.ubigeo for p in preds if p.supera_umbral_algedonico]
        rows = [asdict(r) if not isinstance(r, dict) else r for r in records]
        summary = summarize_parra_luna_panel(rows, s5_ubigeos=s5_ubigeos)
        if not include_all_districts:
            summary = {k: v for k, v in summary.items() if k != "scores_2024"}
            summary["total_distritos_2024"] = len(preds)
        return summary

    @api.get("/evaluation/parra_luna/{ubigeo}", tags=["Semana 7: Evaluación y Gobernanza (AUC, F1, SHAP)"])
    def endpoint_evaluation_parra_luna_district(ubigeo: str) -> Dict[str, Any]:
        """Auditoría axiológica determinista (Regla Fija 4) y progresión 2014->2024 para un distrito."""
        clean_ubigeo = _validate_ubigeo_or_raise(ubigeo)
        records = repo.get_historical_series(anio_inicio=2014, anio_fin=2024)
        if not records:
            tool1.execute(mode="backfill", start_year=2014, end_year=2024, force_rebuild=True)
            records = repo.get_historical_series(anio_inicio=2014, anio_fin=2024)
        rows = [asdict(r) if not isinstance(r, dict) else r for r in records]
        scores_all = compute_parra_luna_scores(rows, reference_rows=rows)
        dist_scores = [s for s in scores_all if s.ubigeo == clean_ubigeo]
        score_2024 = next((s for s in dist_scores if s.anio == 2024), None)
        score_2014 = next((s for s in dist_scores if s.anio == 2014), None)
        if score_2024 is None:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron registros históricos 2024 para el ubigeo '{clean_ubigeo}'.",
            )
        decision = evaluate_axiological_governance_rule(score_2024)
        return {
            "ubigeo": clean_ubigeo,
            "distrito": score_2024.distrito,
            "provincia": score_2024.provincia,
            "perfil_2024": score_2024.to_dict(),
            "perfil_2014": score_2014.to_dict() if score_2014 else None,
            "delta_isdh_geom_2014_2024_pp": (
                round((score_2024.isdh_hvc_geom - score_2014.isdh_hvc_geom) * 100.0, 2)
                if score_2014
                else None
            ),
            "regla_fija_4_equilibrio_axiologico": decision.to_dict(),
        }

    @api.get("/governance/audit", tags=["Semana 7: Evaluación y Gobernanza (AUC, F1, SHAP)"])
    def endpoint_governance_audit() -> Dict[str, Any]:
        """Auditoría consolidada de gobernanza cibernética MSV (Reglas Fijas 1-4, HITL, Ley 29733 y SHA-256)."""
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

        by_channel: Dict[str, int] = {"S5_ALGEDONICO": 0, "S3_CONTROL": 0}
        by_status: Dict[str, int] = {
            "ALGEDONICO_DIRECTO_S5": 0,
            "PENDIENTE_APROBACION": 0,
            "APROBADO_S3": 0,
            "RECHAZADO": 0,
        }
        for a in alerts:
            ch = str(a.get("canal_destino", ""))
            st_val = str(a.get("estado_aprobacion_humana", ""))
            if ch in by_channel:
                by_channel[ch] += 1
            if st_val in by_status:
                by_status[st_val] += 1

        hitl_candidates = by_status["PENDIENTE_APROBACION"] + by_status["APROBADO_S3"] + by_status["RECHAZADO"]
        hitl_resolved = by_status["APROBADO_S3"] + by_status["RECHAZADO"]
        hitl_resolution_rate = round((hitl_resolved / hitl_candidates) * 100.0, 2) if hitl_candidates > 0 else 100.0

        s5_ubigeos = [p.ubigeo for p in preds if p.supera_umbral_algedonico]
        rows = [asdict(r) if not isinstance(r, dict) else r for r in records]
        pl_summary = summarize_parra_luna_panel(rows, s5_ubigeos=s5_ubigeos)
        ax_gov = pl_summary["reglas_axiologicas_gobernanza_2024"]

        return {
            "sistema": "SentinelNutri-HVC (Sistema 4 MSV — GORE Huancavelica)",
            "cumplimiento_ley_29733": {
                "activo": True,
                "politica": "Bloqueo estricto de PII nominal antes de LLM + sanitización defensiva de salida",
            },
            "reglas_fijas_activas": {
                "regla_1_motor_numerico": "CatBoost+SHAP exclusivo (/predict); prohibido cálculo por LLM",
                "regla_2_canal_algedonico_s5": f"DCI proyectada > {ALGEDONIC_DCI_THRESHOLD_PCT:.1f}% -> S5 directo sin bloqueo",
                "regla_3_compuerta_hitl_s3": "Publicación S3 bloqueada hasta aprobación humana nominal (approver_name >= 3 chars)",
                "regla_4_equilibrio_axiologico_parra_luna": ax_gov["regla"],
            },
            "auditoria_alertas_msv": {
                "total_alertas_registradas": len(alerts),
                "alertas_con_huella_sha256_persistida": sum(
                    1 for a in alerts if a.get("huella_auditoria_sha256")
                ),
                "resoluciones_con_huella_sha256_persistida": sum(
                    1 for a in alerts if a.get("huella_resolucion_sha256")
                ),
                "por_canal_msv": by_channel,
                "por_estado_hitl": by_status,
                "tasa_resolucion_hitl_pct": hitl_resolution_rate,
            },
            "trazabilidad_ingesta_sha256": {
                "total_cargas_auditadas": len(loads),
                "fuentes_distintas": sorted({str(ld.get("fuente", "")) for ld in loads if ld.get("fuente")}),
                "ultima_carga": loads[0] if loads else None,
            },
            "gobernanza_axiologica_2024": ax_gov["resumen_estados_2024"],
            "frecuencia_cuello_botella_prvu": ax_gov["frecuencia_cuello_botella_prvu"],
            "distritos_s5_algedonicos_activos": len(s5_ubigeos),
            "distritos_alerta_pre_algedonica": len(ax_gov["distritos_alerta_pre_algedonica"]),
        }

    return api


app = create_app()

