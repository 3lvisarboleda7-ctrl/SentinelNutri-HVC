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

import sqlite3
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from sentinelnutri.application import (
    Tool1ExtraerFuentesUseCase,
    Tool2ConsultarBdUseCase,
    Tool3PredecirRiesgoUseCase,
    Tool4ExplicarRiesgoUseCase,
    Tool5RedactarInformeUseCase,
    Tool6NotificarUseCase,
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

    @api.get("/health", tags=["Infraestructura"])
    def health_check() -> Dict[str, object]:
        districts = repo.get_all_districts()
        return {
            "status": "OK",
            "sistema": "SentinelNutri-HVC (Sistema 4 del MSV - GORE Huancavelica)",
            "distritos_monitoreados": len(districts),
            "umbral_algedonico_fijo_pct": 25.0,
            "cumplimiento_ley_29733": True,
        }

    @api.post("/tools/extraer_fuentes", tags=["Herramientas del Agente Supervisor (Tabla 5)"])
    def endpoint_tool_1_extraer_fuentes(req: ExtraerFuentesRequest) -> Dict[str, object]:
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
    def endpoint_tool_3_predecir_riesgo(req: PredictRequest) -> Dict[str, object]:
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
    def endpoint_tool_6_notificar(req: NotificarRequest) -> Dict[str, Any]:
        try:
            raw_ubigeo = req.report_payload.get("ubigeo", "090101")
            _validate_ubigeo_or_raise(str(raw_ubigeo))
            return tool6.execute_dispatch(report_payload=req.report_payload)
        except HTTPException:
            raise
        except (ValueError, TypeError, sqlite3.IntegrityError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @api.post("/hitl/aprobar/{alert_id}", tags=["Regla Fija 3: Aprobación Humana (HITL)"])
    def endpoint_human_approval(alert_id: int, req: HumanApprovalRequest) -> Dict[str, Any]:
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

    return api


app = create_app()

