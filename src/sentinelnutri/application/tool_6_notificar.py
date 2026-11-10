"""
Herramienta 6 del Agente Supervisor: `notificar` (Tabla 5).
Publica en el Dashboard Streamlit y envía alertas por Telegram y Gmail respetando las Reglas Fijas:
- Si `DCI proyectada > 25 %`: Dispara de inmediato el Canal Algedónico hacia S5 (Consejo Regional)
  sin que el LLM ni demoras administrativas puedan bloquearlo.
- Para el Canal de Control hacia S3 (Gerencia Regional de Desarrollo Social): Registra la propuesta
  en espera de aprobación humana (HITL) y solo la publica como aprobada cuando el responsable
  confirma desde su celular (vía Telegram/Gmail + Cloudflare Tunnel).
"""

from typing import Any, Dict, Optional
from sentinelnutri.domain.entities.alert_msv import ApprovalStatus, MSVAlertReport, MSVChannel
from sentinelnutri.domain.ports.repository_port import RepositoryPort
from sentinelnutri.domain.rules.fixed_thresholds import (
    can_publish_to_s3_control,
    evaluate_fixed_algedonic_rule,
)


class Tool6NotificarUseCase:
    """Caso de uso de Notificación y Enrutamiento Cibernético (S4 -> S3 con HITL y S4 -> S5 Algedónico)."""

    def __init__(
        self,
        repository: RepositoryPort,
        telegram_notifier: Optional[Any] = None,
        gmail_notifier: Optional[Any] = None,
    ) -> None:
        self._repo = repository
        self._telegram = telegram_notifier
        self._gmail = gmail_notifier

    def execute_dispatch(self, report_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evalúa las Reglas Fijas 2 y 3, guarda la alerta en PostgreSQL y despacha las notificaciones.
        """
        ubigeo = str(report_payload.get("ubigeo", "090101"))
        provincia = str(report_payload.get("provincia", "Huancavelica"))
        distrito = str(report_payload.get("distrito", "Huancavelica"))
        dci_proyectada = float(report_payload.get("dci_proyectada_pct", 20.3))

        recs = report_payload.get("recomendaciones_sectoriales", {})
        alin = report_payload.get("alineacion_estrategica", {})

        route_decision = evaluate_fixed_algedonic_rule(ubigeo=ubigeo, dci_proyectada_pct=dci_proyectada)

        algedonic_dispatched = False
        if route_decision.supera_umbral_critico:
            # REGLA FIJA 2: El canal algedónico hacia S5 se dispara SIEMPRE que DCI proyectada > 25%
            initial_status = ApprovalStatus.ALGEDONICO_DIRECTO_S5
            algedonic_dispatched = True
            if self._telegram:
                self._telegram.send_algedonic_alert_s5(
                    ubigeo=ubigeo,
                    provincia=provincia,
                    distrito=distrito,
                    dci_proyectada_pct=dci_proyectada,
                    sintesis=str(report_payload.get("sintesis_narrativa_s4", "")),
                )
            if self._gmail:
                self._gmail.send_algedonic_email_s5(
                    ubigeo=ubigeo,
                    provincia=provincia,
                    distrito=distrito,
                    dci_proyectada_pct=dci_proyectada,
                    sintesis=str(report_payload.get("sintesis_narrativa_s4", "")),
                )
        else:
            # REGLA FIJA 3: Hacia S3 queda en espera de aprobación humana (Telegram / Gmail con respuesta)
            initial_status = ApprovalStatus.PENDIENTE_APROBACION

        alert_entity = MSVAlertReport(
            ubigeo=ubigeo,
            provincia=provincia,
            distrito=distrito,
            nivel_riesgo="CRITICO" if route_decision.supera_umbral_critico else "MODERADO_ALTO",
            dci_proyectada_pct=dci_proyectada,
            canal_destino=route_decision.canal_obligatorio,
            sintesis_narrativa_s4=str(report_payload.get("sintesis_narrativa_s4", "")),
            recomendacion_salud=str(recs.get("salud_diresa", "")),
            recomendacion_agua_saneamiento=str(recs.get("agua_saneamiento_drvcs", "")),
            recomendacion_agricultura_midis=str(recs.get("agricultura_midis_mef", "")),
            oei_pei_vinculados=str(alin.get("pei_gore_huancavelica_2020_2027", "OEI.01, OEI.04, OEI.08")),
            ods_vinculados=str(alin.get("agenda_2030_ods", "ODS 2, ODS 3, ODS 6")),
            proveedor_llm=str(report_payload.get("proveedor_llm_utilizado", "gemini-2.0-flash")),
            estado_aprobacion_humana=initial_status,
        )

        alert_id = self._repo.save_alert_report(alert_entity)

        return {
            "tool": "notificar",
            "id_alerta": alert_id,
            "ubigeo": ubigeo,
            "distrito": distrito,
            "dci_proyectada_pct": dci_proyectada,
            "regla_fija_algedonica_activada_s5": algedonic_dispatched,
            "canal_destino": route_decision.canal_obligatorio.value,
            "estado_aprobacion_humana": initial_status.value,
            "publicado_en_canal_control_s3": can_publish_to_s3_control(initial_status),
            "mensaje": (
                "Señal algedónica enviada directamente al S5 (Consejo Regional) por superar 25 % de DCI proyectada; "
                "recomendación enviada a aprobación humana para el S3."
                if algedonic_dispatched
                else "Recomendación registrada y enviada por Telegram/Gmail esperando aprobación humana antes de publicar en S3."
            ),
        }

    def resolve_human_approval(
        self,
        alert_id: int,
        approved: bool,
        approver_name: str = "Responsable GRDS-S3 (vía Celular / Cloudflare Tunnel)",
    ) -> Dict[str, Any]:
        """
        Procesa el webhook de respuesta humana (Evento E6: HumanApprovalResolved).
        Solo si `approved=True`, libera la recomendación hacia el Canal de Control S3 (Dashboard Streamlit).
        """
        clean_approver = str(approver_name).strip() if approver_name is not None else ""
        if not clean_approver:
            raise ValueError(
                "Regla Fija 3 (HITL): El nombre de la autoridad aprobadora (approver_name) no puede estar vacío."
            )

        new_status = ApprovalStatus.APROBADO_S3 if approved else ApprovalStatus.RECHAZADO
        updated = self._repo.update_alert_approval(
            alert_id=alert_id,
            status=new_status,
            approved_by=clean_approver,
        )
        if not updated:
            raise ValueError(f"No se encontró la alerta con ID {alert_id}.")

        return {
            "id_alerta": alert_id,
            "ubigeo": updated.ubigeo,
            "distrito": updated.distrito,
            "estado_aprobacion_humana": updated.estado_aprobacion_humana.value,
            "aprobado_por": updated.aprobado_por,
            "publicado_en_canal_control_s3": can_publish_to_s3_control(updated.estado_aprobacion_humana),
        }

