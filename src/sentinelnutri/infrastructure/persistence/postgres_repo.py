"""Implementación Relacional del Puerto `RepositoryPort` (Compatible con SQLite/PostgreSQL)."""

from datetime import datetime, timezone
import json
import sqlite3
from typing import Callable, Dict, List, Optional
from sentinelnutri.domain.entities.alert_msv import ApprovalStatus, MSVAlertReport, MSVChannel
from sentinelnutri.domain.entities.district import DistrictIndicatorRecord, DistrictMetadata
from sentinelnutri.domain.entities.prediction import DistrictRiskPrediction, RiskLevel, ShapContribution
from sentinelnutri.domain.ports.repository_port import RepositoryPort


def _now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


class SqlAlchemyRepository(RepositoryPort):
    """Adaptador relacional SQL que implementa todos los contratos del MSV."""

    def __init__(self, connection_factory: Callable[[], sqlite3.Connection]) -> None:
        self._get_conn = connection_factory

    def get_all_districts(self) -> List[DistrictMetadata]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM cat_ubigeo_hvc ORDER BY ubigeo").fetchall()
            return [
                DistrictMetadata(
                    ubigeo=r["ubigeo"],
                    provincia=r["provincia"],
                    distrito=r["distrito"],
                    red_salud=r["red_salud"],
                    altitud_msnm=int(r["altitud_msnm"]),
                    latitud=float(r["latitud"]),
                    longitud=float(r["longitud"]),
                    poblacion_menor_5=int(r["poblacion_menor_5"]),
                    ruralidad_pct=float(r["ruralidad_pct"]),
                )
                for r in rows
            ]

    def get_latest_load_hash(self, fuente: str, url_origen: str) -> Optional[str]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT hash_sha256 FROM registro_cargas WHERE fuente = ? AND url_origen = ? ORDER BY id DESC LIMIT 1",
                (fuente, url_origen),
            ).fetchone()
            return row["hash_sha256"] if row else None

    def register_load_attempt(
        self,
        fuente: str,
        url_origen: str,
        hash_sha256: str,
        hubo_cambio: bool,
        ruta_archivo_crudo: str,
        registros_procesados: int,
        estado: str = "OK",
        detalle_mensaje: str = "",
    ) -> Dict[str, object]:
        now = _now_str()
        with self._get_conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO registro_cargas (
                    fuente, url_origen, fecha_publicacion_portal, fecha_consulta,
                    hash_sha256, hubo_cambio, ruta_archivo_crudo, registros_procesados,
                    estado, detalle_mensaje
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fuente,
                    url_origen,
                    now[:10],
                    now,
                    hash_sha256,
                    bool(hubo_cambio),
                    ruta_archivo_crudo,
                    registros_procesados,
                    estado,
                    detalle_mensaje,
                ),
            )
            conn.commit()
            return {
                "id": cur.lastrowid,
                "fuente": fuente,
                "hash_sha256": hash_sha256,
                "hubo_cambio": hubo_cambio,
                "estado": estado,
            }

    def get_recent_loads(self, limit: int = 25) -> List[Dict[str, object]]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM registro_cargas ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [
                {
                    "id": r["id"],
                    "fuente": r["fuente"],
                    "url_origen": r["url_origen"],
                    "fecha_consulta": r["fecha_consulta"],
                    "hash_sha256": r["hash_sha256"][:16] + "...",
                    "hubo_cambio": bool(r["hubo_cambio"]),
                    "ruta_archivo_crudo": r["ruta_archivo_crudo"],
                    "registros_procesados": r["registros_procesados"],
                    "estado": r["estado"],
                    "detalle_mensaje": r["detalle_mensaje"],
                }
                for r in rows
            ]

    def upsert_historical_records(self, records: List[DistrictIndicatorRecord]) -> int:
        with self._get_conn() as conn:
            conn.executemany(
                """
                INSERT INTO serie_historica_distrital (
                    ubigeo, anio, semestre, tasa_dci_pct, tasa_anemia_pct, tasa_bajo_peso_pct,
                    ninos_evaluados, pobreza_monetaria_pct, educacion_materna_secundaria_pct,
                    agua_cloro_adecuado_pct, saneamiento_basico_pct, controles_cred_completo_pct,
                    lactancia_materna_exclusiva_pct, ejecucion_pan_mef_pct, presupuesto_pan_per_capita_soles,
                    cobertura_juntos_pct, cobertura_cuna_mas_pct, cobertura_qali_warma_pct,
                    dias_heladas_anual, temp_minima_promedio_c, precipitacion_anual_mm
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(ubigeo, anio, semestre) DO UPDATE SET
                    tasa_dci_pct=excluded.tasa_dci_pct,
                    tasa_anemia_pct=excluded.tasa_anemia_pct,
                    tasa_bajo_peso_pct=excluded.tasa_bajo_peso_pct,
                    ninos_evaluados=excluded.ninos_evaluados,
                    pobreza_monetaria_pct=excluded.pobreza_monetaria_pct,
                    educacion_materna_secundaria_pct=excluded.educacion_materna_secundaria_pct,
                    agua_cloro_adecuado_pct=excluded.agua_cloro_adecuado_pct,
                    saneamiento_basico_pct=excluded.saneamiento_basico_pct,
                    controles_cred_completo_pct=excluded.controles_cred_completo_pct,
                    lactancia_materna_exclusiva_pct=excluded.lactancia_materna_exclusiva_pct,
                    ejecucion_pan_mef_pct=excluded.ejecucion_pan_mef_pct,
                    presupuesto_pan_per_capita_soles=excluded.presupuesto_pan_per_capita_soles,
                    cobertura_juntos_pct=excluded.cobertura_juntos_pct,
                    cobertura_cuna_mas_pct=excluded.cobertura_cuna_mas_pct,
                    cobertura_qali_warma_pct=excluded.cobertura_qali_warma_pct,
                    dias_heladas_anual=excluded.dias_heladas_anual,
                    temp_minima_promedio_c=excluded.temp_minima_promedio_c,
                    precipitacion_anual_mm=excluded.precipitacion_anual_mm
                """,
                [
                    (
                        r.ubigeo,
                        r.anio,
                        r.semestre,
                        r.tasa_dci_pct,
                        r.tasa_anemia_pct,
                        r.tasa_bajo_peso_pct,
                        r.ninos_evaluados,
                        r.pobreza_monetaria_pct,
                        r.educacion_materna_secundaria_pct,
                        r.agua_cloro_adecuado_pct,
                        r.saneamiento_basico_pct,
                        r.controles_cred_completo_pct,
                        r.lactancia_materna_exclusiva_pct,
                        r.ejecucion_pan_mef_pct,
                        r.presupuesto_pan_per_capita_soles,
                        r.cobertura_juntos_pct,
                        r.cobertura_cuna_mas_pct,
                        r.cobertura_qali_warma_pct,
                        r.dias_heladas_anual,
                        r.temp_minima_promedio_c,
                        r.precipitacion_anual_mm,
                    )
                    for r in records
                ],
            )
            conn.commit()
        return len(records)

    def get_historical_series(
        self,
        ubigeo: Optional[str] = None,
        anio_inicio: int = 2014,
        anio_fin: int = 2025,
    ) -> List[DistrictIndicatorRecord]:
        with self._get_conn() as conn:
            if ubigeo:
                rows = conn.execute(
                    """
                    SELECT s.*, c.provincia, c.distrito, c.red_salud, c.altitud_msnm, c.ruralidad_pct
                    FROM serie_historica_distrital s
                    JOIN cat_ubigeo_hvc c ON s.ubigeo = c.ubigeo
                    WHERE s.ubigeo = ? AND s.anio >= ? AND s.anio <= ?
                    ORDER BY s.ubigeo, s.anio
                    """,
                    (ubigeo, anio_inicio, anio_fin),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT s.*, c.provincia, c.distrito, c.red_salud, c.altitud_msnm, c.ruralidad_pct
                    FROM serie_historica_distrital s
                    JOIN cat_ubigeo_hvc c ON s.ubigeo = c.ubigeo
                    WHERE s.anio >= ? AND s.anio <= ?
                    ORDER BY s.ubigeo, s.anio
                    """,
                    (anio_inicio, anio_fin),
                ).fetchall()

            return [
                DistrictIndicatorRecord(
                    ubigeo=r["ubigeo"],
                    anio=int(r["anio"]),
                    semestre=int(r["semestre"]),
                    tasa_dci_pct=float(r["tasa_dci_pct"]),
                    tasa_anemia_pct=float(r["tasa_anemia_pct"]),
                    tasa_bajo_peso_pct=float(r["tasa_bajo_peso_pct"]),
                    ninos_evaluados=int(r["ninos_evaluados"]),
                    pobreza_monetaria_pct=float(r["pobreza_monetaria_pct"]),
                    educacion_materna_secundaria_pct=float(r["educacion_materna_secundaria_pct"]),
                    agua_cloro_adecuado_pct=float(r["agua_cloro_adecuado_pct"]),
                    saneamiento_basico_pct=float(r["saneamiento_basico_pct"]),
                    controles_cred_completo_pct=float(r["controles_cred_completo_pct"]),
                    lactancia_materna_exclusiva_pct=float(r["lactancia_materna_exclusiva_pct"]),
                    ejecucion_pan_mef_pct=float(r["ejecucion_pan_mef_pct"]),
                    presupuesto_pan_per_capita_soles=float(r["presupuesto_pan_per_capita_soles"]),
                    cobertura_juntos_pct=float(r["cobertura_juntos_pct"]),
                    cobertura_cuna_mas_pct=float(r["cobertura_cuna_mas_pct"]),
                    cobertura_qali_warma_pct=float(r["cobertura_qali_warma_pct"]),
                    dias_heladas_anual=int(r["dias_heladas_anual"]),
                    temp_minima_promedio_c=float(r["temp_minima_promedio_c"]),
                    precipitacion_anual_mm=float(r["precipitacion_anual_mm"]),
                    provincia=r["provincia"],
                    distrito=r["distrito"],
                    red_salud=r["red_salud"],
                    altitud_msnm=int(r["altitud_msnm"]),
                    ruralidad_pct=float(r["ruralidad_pct"]),
                )
                for r in rows
            ]

    def save_prediction(self, prediction: DistrictRiskPrediction) -> int:
        top_summary = "; ".join(
            f"{c.etiqueta_legible} ({c.valor_shap:+.2f})" for c in prediction.top_contribuciones_shap[:3]
        )
        shap_payload = {
            "raw": prediction.valores_shap,
            "top": [
                {
                    "variable": c.variable,
                    "etiqueta_legible": c.etiqueta_legible,
                    "valor_observado": c.valor_observado,
                    "valor_shap": c.valor_shap,
                    "direccion_impacto": c.direccion_impacto,
                }
                for c in prediction.top_contribuciones_shap
            ],
        }
        with self._get_conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO predicciones_dci (
                    ubigeo, anio_base, horizonte_proyeccion, dci_actual_pct,
                    dci_proyectada_pct, probabilidad_riesgo_critico, nivel_riesgo,
                    supera_umbral_algedonico, valores_shap_json, top_factores_riesgo,
                    version_modelo, fecha_prediccion
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    prediction.ubigeo,
                    prediction.anio_base,
                    "PROXIMO_SEMESTRE",
                    prediction.dci_actual_pct,
                    prediction.dci_proyectada_pct,
                    prediction.probabilidad_riesgo_critico,
                    prediction.nivel_riesgo.value,
                    bool(prediction.supera_umbral_algedonico),
                    json.dumps(shap_payload, ensure_ascii=False),
                    top_summary,
                    prediction.version_modelo,
                    _now_str(),
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

    def get_latest_predictions(self, provincia: Optional[str] = None) -> List[DistrictRiskPrediction]:
        with self._get_conn() as conn:
            if provincia:
                rows = conn.execute(
                    """
                    SELECT p.*, c.provincia, c.distrito, c.red_salud
                    FROM predicciones_dci p
                    JOIN (
                        SELECT ubigeo, MAX(id) AS max_id
                        FROM predicciones_dci
                        GROUP BY ubigeo
                    ) latest ON p.id = latest.max_id
                    JOIN cat_ubigeo_hvc c ON p.ubigeo = c.ubigeo
                    WHERE c.provincia = ?
                    ORDER BY p.dci_proyectada_pct DESC
                    """,
                    (provincia,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT p.*, c.provincia, c.distrito, c.red_salud
                    FROM predicciones_dci p
                    JOIN (
                        SELECT ubigeo, MAX(id) AS max_id
                        FROM predicciones_dci
                        GROUP BY ubigeo
                    ) latest ON p.id = latest.max_id
                    JOIN cat_ubigeo_hvc c ON p.ubigeo = c.ubigeo
                    ORDER BY p.dci_proyectada_pct DESC
                    """
                ).fetchall()

            result: List[DistrictRiskPrediction] = []
            for r in rows:
                parsed = json.loads(r["valores_shap_json"]) if r["valores_shap_json"] else {"raw": {}, "top": []}
                top_contribs = [
                    ShapContribution(
                        variable=item["variable"],
                        etiqueta_legible=item["etiqueta_legible"],
                        valor_observado=float(item["valor_observado"]),
                        valor_shap=float(item["valor_shap"]),
                        direccion_impacto=item["direccion_impacto"],
                    )
                    for item in parsed.get("top", [])
                ]
                result.append(
                    DistrictRiskPrediction(
                        ubigeo=r["ubigeo"],
                        provincia=r["provincia"],
                        distrito=r["distrito"],
                        red_salud=r["red_salud"],
                        anio_base=int(r["anio_base"]),
                        dci_actual_pct=float(r["dci_actual_pct"]),
                        dci_proyectada_pct=float(r["dci_proyectada_pct"]),
                        probabilidad_riesgo_critico=float(r["probabilidad_riesgo_critico"]),
                        nivel_riesgo=RiskLevel(r["nivel_riesgo"]),
                        supera_umbral_algedonico=bool(r["supera_umbral_algedonico"]),
                        valores_shap=parsed.get("raw", {}),
                        top_contribuciones_shap=top_contribs,
                        version_modelo=r["version_modelo"],
                    )
                )
            return result

    def save_alert_report(self, report: MSVAlertReport) -> int:
        with self._get_conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO alertas_y_recomendaciones_msv (
                    ubigeo, provincia, nivel_riesgo, canal_destino, sintesis_narrativa_s4,
                    recomendacion_salud, recomendacion_agua_saneamiento, recomendacion_agricultura_midis,
                    oei_pei_vinculados, ods_vinculados, proveedor_llm, estado_aprobacion_humana,
                    aprobado_por, fecha_creacion
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    report.ubigeo,
                    report.provincia,
                    report.nivel_riesgo,
                    report.canal_destino.value,
                    report.sintesis_narrativa_s4,
                    report.recomendacion_salud,
                    report.recomendacion_agua_saneamiento,
                    report.recomendacion_agricultura_midis,
                    report.oei_pei_vinculados,
                    report.ods_vinculados,
                    report.proveedor_llm,
                    report.estado_aprobacion_humana.value,
                    report.aprobado_por,
                    _now_str(),
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

    def update_alert_approval(
        self,
        alert_id: int,
        status: ApprovalStatus,
        approved_by: str,
    ) -> Optional[MSVAlertReport]:
        with self._get_conn() as conn:
            conn.execute(
                """
                UPDATE alertas_y_recomendaciones_msv
                SET estado_aprobacion_humana = ?, aprobado_por = ?, fecha_resolucion = ?
                WHERE id = ?
                """,
                (status.value, approved_by, _now_str(), alert_id),
            )
            conn.commit()
            row = conn.execute(
                """
                SELECT a.*, c.distrito
                FROM alertas_y_recomendaciones_msv a
                JOIN cat_ubigeo_hvc c ON a.ubigeo = c.ubigeo
                WHERE a.id = ?
                """,
                (alert_id,),
            ).fetchone()
            if not row:
                return None
            return MSVAlertReport(
                id_alerta=int(row["id"]),
                ubigeo=row["ubigeo"],
                provincia=row["provincia"],
                distrito=row["distrito"],
                nivel_riesgo=row["nivel_riesgo"],
                dci_proyectada_pct=26.0 if row["canal_destino"] == "S5_ALGEDONICO" else 19.5,
                canal_destino=MSVChannel(row["canal_destino"]),
                sintesis_narrativa_s4=row["sintesis_narrativa_s4"],
                recomendacion_salud=row["recomendacion_salud"],
                recomendacion_agua_saneamiento=row["recomendacion_agua_saneamiento"],
                recomendacion_agricultura_midis=row["recomendacion_agricultura_midis"],
                oei_pei_vinculados=row["oei_pei_vinculados"],
                ods_vinculados=row["ods_vinculados"],
                proveedor_llm=row["proveedor_llm"],
                estado_aprobacion_humana=ApprovalStatus(row["estado_aprobacion_humana"]),
                aprobado_por=row["aprobado_por"],
            )

    def get_all_alerts(self) -> List[Dict[str, object]]:
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT a.*, c.distrito, c.red_salud
                FROM alertas_y_recomendaciones_msv a
                JOIN cat_ubigeo_hvc c ON a.ubigeo = c.ubigeo
                ORDER BY a.id DESC
                """
            ).fetchall()
            return [dict(r) for r in rows]
