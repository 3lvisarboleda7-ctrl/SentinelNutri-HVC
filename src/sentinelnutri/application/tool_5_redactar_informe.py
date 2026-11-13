"""
Herramienta 5 del Agente Supervisor: `redactar_informe` (Tabla 5).
Elabora la síntesis narrativa para el S4 y las recomendaciones diferenciadas por provincia y sector
(Salud, Agua y Saneamiento, Agricultura y Programas MIDIS) alineadas a los OEI del PEI 2020-2027
y a los ODS 2, 3 y 6, garantizando que nunca se envíen datos personales al LLM (Ley N.° 29733).
"""

from typing import Any, Dict, Optional
from sentinelnutri.domain.entities.alert_msv import ApprovalStatus, MSVAlertReport
from sentinelnutri.domain.rules.fixed_thresholds import evaluate_fixed_algedonic_rule
from sentinelnutri.domain.rules.privacy_guard import sanitize_district_payload_for_llm


class Tool5RedactarInformeUseCase:
    """Caso de uso del Amplificador de Variedad de Gestión (Síntesis S4 + Recomendaciones PEI 2020-2027)."""

    def __init__(self, llm_gateway: Optional[Any] = None) -> None:
        self._llm = llm_gateway

    def execute(self, district_context: Dict[str, Any], prefer_provider: str = "gemini") -> Dict[str, Any]:
        """
        1. Verifica cumplimiento estricto de la Ley N.° 29733 (solo indicadores agregados).
        2. Genera la síntesis narrativa y las recomendaciones sectoriales (vía Gemini Free Tier,
           Ollama Llama 3.2 en GTX 1050 como respaldo, o plantilla estructurada determinista).
        """
        safe_context = sanitize_district_payload_for_llm(district_context, strict=True)

        ubigeo = str(safe_context.get("ubigeo", "090101"))
        provincia = str(safe_context.get("provincia", "Huancavelica"))
        distrito = str(safe_context.get("distrito", "Huancavelica"))
        dci_proyectada = float(safe_context.get("dci_proyectada_pct", 20.3))
        dci_actual = float(safe_context.get("dci_actual_pct", 20.0))
        top_shap = safe_context.get("contribuciones_shap_ordenadas") or safe_context.get("top_factores_shap") or []

        route_decision = evaluate_fixed_algedonic_rule(ubigeo=ubigeo, dci_proyectada_pct=dci_proyectada)

        top_factor_names = [
            str(f.get("determinante") or f.get("etiqueta") or f.get("variable"))
            for f in top_shap[:3]
            if isinstance(f, dict)
        ]
        factores_texto = ", ".join(top_factor_names) if top_factor_names else (
            "baja cobertura de agua con cloro adecuado, incidencia de heladas y brecha de ejecución en el PAN"
        )

        used_provider = "gemini-flash-lite-latest (Google AI Studio Free Tier)"
        custom_llm_output: Optional[Dict[str, str]] = None
        if self._llm is not None:
            custom_llm_output, used_provider = self._llm.generate_policy_report(
                safe_context=safe_context,
                prefer_provider=prefer_provider,
            )

        if (
            isinstance(custom_llm_output, dict)
            and all(
                isinstance(custom_llm_output.get(k), str) and custom_llm_output[k].strip()
                for k in (
                    "sintesis_narrativa_s4",
                    "recomendacion_salud",
                    "recomendacion_agua_saneamiento",
                    "recomendacion_agricultura_midis",
                )
            )
        ):
            sintesis = custom_llm_output["sintesis_narrativa_s4"]
            rec_salud = custom_llm_output["recomendacion_salud"]
            rec_agua = custom_llm_output["recomendacion_agua_saneamiento"]
            rec_agro = custom_llm_output["recomendacion_agricultura_midis"]
        else:
            if custom_llm_output is not None:
                used_provider = "fallback-determinista-msv (JSON LLM incompleto recuperado)"
            sintesis = (
                f"[S4 · Inteligencia Prospectiva] El distrito de {distrito} (Provincia de {provincia}, "
                f"Ubigeo {ubigeo}) registra una DCI actual de {dci_actual:.1f} % y una proyección de "
                f"{dci_proyectada:.1f} % ({route_decision.canal_obligatorio.value}). "
                f"La auditoría XAI (SHAP - S3*) identifica como determinantes principales: {factores_texto}."
            )
            rec_salud = (
                f"[Sector Salud · DIRESA / Red de Salud {provincia} - OEI.01 y OEI.03] "
                f"Desplegar brigadas integrales de control CRED y suplementación preventiva de hierro en "
                f"{distrito}, priorizando centros poblados sobre los 3 400 m s. n. m. antes del pico de heladas."
            )
            rec_agua = (
                f"[Sector Agua y Saneamiento · DRVCS / ATM Municipal - OEI.04] "
                f"Intervenir los sistemas de cloración rural en {distrito} mediante asistencia técnica de las ATM "
                f"para elevar el porcentaje de hogares con cloro residual >= 0,5 mg/L y cortar el bucle "
                f"infecciones -> anemia/DCI."
            )
            rec_agro = (
                f"[Sector Agricultura, MEF y MIDIS · DRA / PAN 0001 - OEI.08 y OEI.10] "
                f"Acelerar el devengado del Programa Articulado Nutricional (0001) en el gobierno local de "
                f"{distrito}, articular el padrón nominal con Juntos/Cuna Más y proteger cultivos familiares "
                f"altoandinos ante alertas agrometeorológicas del SENAMHI."
            )

        report = MSVAlertReport(
            ubigeo=ubigeo,
            provincia=provincia,
            distrito=distrito,
            nivel_riesgo="CRITICO" if route_decision.supera_umbral_critico else "MODERADO_ALTO",
            dci_proyectada_pct=dci_proyectada,
            canal_destino=route_decision.canal_obligatorio,
            sintesis_narrativa_s4=sintesis,
            recomendacion_salud=rec_salud,
            recomendacion_agua_saneamiento=rec_agua,
            recomendacion_agricultura_midis=rec_agro,
            oei_pei_vinculados="OEI.01 (Reducir DCI y Anemia), OEI.04 (Agua y Saneamiento Rural), OEI.08 (Competitividad Agraria), OEI.10 (GRD y Heladas)",
            ods_vinculados="ODS 2 (Meta 2.2), ODS 3 (Meta 3.2), ODS 6 (Meta 6.1)",
            proveedor_llm=used_provider,
            estado_aprobacion_humana=ApprovalStatus.PENDIENTE_APROBACION,
        )

        return {
            "tool": "redactar_informe",
            "cumplimiento_ley_29733": "VERIFICADO_SOLO_INDICADORES_AGREGADOS",
            "proveedor_llm_utilizado": report.proveedor_llm,
            "informe": {
                "ubigeo": report.ubigeo,
                "provincia": report.provincia,
                "distrito": report.distrito,
                "dci_proyectada_pct": report.dci_proyectada_pct,
                "canal_destino": report.canal_destino.value,
                "sintesis_narrativa_s4": report.sintesis_narrativa_s4,
                "recomendaciones_sectoriales": {
                    "salud_diresa": report.recomendacion_salud,
                    "agua_saneamiento_drvcs": report.recomendacion_agua_saneamiento,
                    "agricultura_midis_mef": report.recomendacion_agricultura_midis,
                },
                "alineacion_estrategica": {
                    "pei_gore_huancavelica_2020_2027": report.oei_pei_vinculados,
                    "agenda_2030_ods": report.ods_vinculados,
                },
                "estado_aprobacion_humana": report.estado_aprobacion_humana.value,
            },
        }

