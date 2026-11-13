"""
Ensayo de Demostración Flujo End-to-End (E2E) en Vivo — SentinelNutri-HVC.

Ejecuta desde el Equipo 1 contra el Servidor Local (Equipo 2 vía LAN) la cadena completa del MSV:
1. Conectividad de servicios Docker + GPU (`FastAPI :8000`, `Ollama GTX 1050 :11434`, `n8n :5678`, `Streamlit :8501`).
2. Herramienta 1 (`extraer_fuentes` en modo `weekly_watch`) + trazabilidad `SHA-256`.
3. Herramienta 2 (`consultar_bd` 2014–2024) y validación de desempeño (`AUC-ROC >= 0,90`).
4. Herramienta 3 (`predecir_riesgo` / `CatBoost /predict`) + Reglas Fijas 1 y 2 (`> 25 % -> S5`).
5. Herramienta 4 (`explicar_riesgo` SHAP) para soporte a Auditoría `S3*`.
6. Guardarraíl Ley N.º 29733 (`HTTP 422` ante datos nominales) + Herramienta 5 (`redactar_informe` Gemini / Ollama).
7. Herramienta 6 (`notificar`) + Regla Fija 2 (`S5_ALGEDONICO`) + Regla Fija 3 (`HITL S3 -> /hitl/aprobar/{id}`).
"""

import argparse
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Tuple


def _read_equipo2_ip_from_env() -> str:
    env_path = Path("config/.env.equipo1")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            clean = line.strip()
            if clean.startswith("EQUIPO2_LAN_IP="):
                return clean.split("=", 1)[1].strip().strip('"')
    return os.getenv("EQUIPO2_LAN_IP", "192.168.1.6")


def _http_json(
    url: str,
    method: str = "GET",
    payload: Dict[str, Any] | None = None,
    timeout: float = 20.0,
) -> Tuple[int, Any]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as exc:
        raw_err = exc.read().decode("utf-8", errors="replace")
        try:
            return exc.code, json.loads(raw_err)
        except json.JSONDecodeError:
            return exc.code, raw_err


def _step(num: int, title: str) -> None:
    print(f"\n=== [{num}/7] {title} ===")


def run_rehearsal(host: str) -> int:
    api_base = f"http://{host}:8000"
    ollama_base = f"http://{host}:11434"
    n8n_base = f"http://{host}:5678"
    streamlit_base = f"http://{host}:8501"
    t0_total = time.perf_counter()

    _step(1, f"Verificación de Infraestructura Dual (Equipo 1 -> LAN {host})")
    code, health = _http_json(f"{api_base}/health")
    assert code == 200 and health.get("status") == "OK", f"FastAPI falló: {code} {health}"
    print(
        f"[OK] FastAPI ({api_base}): {health['distritos_monitoreados']} distritos | "
        f"Umbral S5={health['umbral_algedonico_fijo_pct']}% | Ley29733={health['cumplimiento_ley_29733']}"
    )

    code_ol, ol_tags = _http_json(f"{ollama_base}/api/tags", timeout=5.0)
    assert code_ol == 200, f"Ollama falló: {code_ol}"
    models = [m.get("name") for m in ol_tags.get("models", [])]
    print(f"[OK] Ollama GPU GTX 1050 ({ollama_base}): modelos={models}")

    code_n8n, n8n_health = _http_json(f"{n8n_base}/healthz", timeout=5.0)
    assert code_n8n == 200, f"n8n falló: {code_n8n}"
    print(f"[OK] n8n Supervisor ({n8n_base}): {n8n_health}")

    code_st, st_health = _http_json(f"{streamlit_base}/_stcore/health", timeout=5.0)
    assert code_st == 200, f"Streamlit falló: {code_st}"
    print(f"[OK] Dashboard Streamlit ({streamlit_base}): {st_health}")

    _step(2, "Tool 1 (`extraer_fuentes` weekly_watch) + Tool 2 (`consultar_bd`) + Métricas")
    code, res1 = _http_json(
        f"{api_base}/tools/extraer_fuentes",
        method="POST",
        payload={"mode": "weekly_watch", "start_year": 2014, "end_year": 2024, "force_rebuild": False},
    )
    assert code == 200, f"Tool 1 falló: {code} {res1}"
    print(f"[OK] Tool 1: portales={res1.get('portales_consultados')} | modo={res1.get('mode')}")

    code, res2 = _http_json(f"{api_base}/tools/consultar_bd?anio_inicio=2014&anio_fin=2024")
    assert code == 200 and res2.get("total_distritos_catalogo") == 100, f"Tool 2 falló: {code}"
    print(
        f"[OK] Tool 2: catálogo={res2['total_distritos_catalogo']} distritos | "
        f"series={res2['total_registros_serie']} registros (2014–2024)"
    )

    code, metrics = _http_json(f"{api_base}/evaluation/metrics")
    assert code == 200 and metrics["metricas_globales"]["cumple_meta_auc_090"], f"Metrics falló: {code}"
    mg = metrics["metricas_globales"]
    print(
        f"[OK] Validación XAI: AUC-ROC={mg['auc_roc']} (>=0.90) | F1={mg['f1_score']} | "
        f"Recall={mg['recall']} | Accuracy={mg['accuracy']}"
    )

    _step(3, "Tool 3 (`CatBoost /predict`) + Reglas Fijas 1 y 2 (Umbral Algedónico 25%)")
    t_pred = time.perf_counter()
    code, res3 = _http_json(f"{api_base}/predict", method="POST", payload={"anio_corte": 2024})
    dt_pred = time.perf_counter() - t_pred
    assert code == 200 and res3.get("total_distritos_evaluados") == 100, f"Predict falló: {code}"
    criticos = res3.get("distritos_criticos_s5", [])
    assert len(criticos) >= 1, "Debe haber al menos 1 distrito crítico > 25% para probar S5"
    critico = criticos[0]
    control = next(p for p in res3["predicciones_distritales"] if not p["supera_umbral_algedonico_25pct"])
    print(
        f"[OK] Tool 3 ({dt_pred:.2f}s): {res3['total_distritos_evaluados']} distritos | "
        f"Alertas S5 (>25%)={len(criticos)}"
    )
    print(
        f"     - Caso Crítico S5: {critico['distrito']} ({critico['ubigeo']}) -> "
        f"DCI Proy={critico['dci_proyectada_pct']}% -> {critico['canal_msv_asignado']}"
    )
    print(
        f"     - Caso Control S3: {control['distrito']} ({control['ubigeo']}) -> "
        f"DCI Proy={control['dci_proyectada_pct']}% -> {control['canal_msv_asignado']}"
    )

    _step(4, "Tool 4 (`explicar_riesgo` SHAP para Auditoría S3*)")
    code, exp_s5 = _http_json(f"{api_base}/tools/explicar_riesgo/{critico['ubigeo']}")
    assert code == 200, f"Tool 4 S5 falló: {code}"
    top_s5 = exp_s5["contribuciones_shap_ordenadas"][0]
    print(
        f"[OK] Auditoría S3* ({critico['distrito']}): Top SHAP = {top_s5['determinante']} "
        f"({top_s5['aporte_shap_puntos_pct']:+.2f} pp)"
    )

    code, exp_s3 = _http_json(f"{api_base}/tools/explicar_riesgo/{control['ubigeo']}")
    assert code == 200, f"Tool 4 S3 falló: {code}"
    top_s3 = exp_s3["contribuciones_shap_ordenadas"][0]
    print(
        f"[OK] Auditoría S3* ({control['distrito']}): Top SHAP = {top_s3['determinante']} "
        f"({top_s3['aporte_shap_puntos_pct']:+.2f} pp)"
    )

    _step(5, "Guardarraíl Ley N.º 29733 (Bloqueo Datos Nominales) + Tool 5 (Gemini / Ollama)")
    code_priv, priv_resp = _http_json(
        f"{api_base}/tools/redactar_informe",
        method="POST",
        payload={"district_context": {"ubigeo": critico["ubigeo"], "dni": "44556677", "nombres": "Nino Prueba"}},
    )
    assert code_priv == 422, f"Se esperaba HTTP 422 por Ley 29733, se obtuvo {code_priv}: {priv_resp}"
    print(f"[OK] Ley N.º 29733 bloqueó dato nominal ('dni') con HTTP 422.")

    code_g, rep_s5 = _http_json(
        f"{api_base}/tools/redactar_informe",
        method="POST",
        payload={"district_context": exp_s5, "prefer_provider": "gemini"},
        timeout=60.0,
    )
    assert code_g == 200, f"Tool 5 Gemini falló: {code_g} {rep_s5}"
    prov_g = str(rep_s5.get("proveedor_llm_utilizado", ""))
    tag_g = "WARN" if "Síntesis Estructurada Local" in prov_g else "OK"
    print(f"[{tag_g}] Tool 5 S5 (prefer=gemini): proveedor real={prov_g}")

    code_o, rep_s3 = _http_json(
        f"{api_base}/tools/redactar_informe",
        method="POST",
        payload={"district_context": exp_s3, "prefer_provider": "ollama"},
        timeout=60.0,
    )
    assert code_o == 200, f"Tool 5 Ollama falló: {code_o} {rep_s3}"
    prov_o = str(rep_s3.get("proveedor_llm_utilizado", ""))
    tag_o = "WARN" if "Síntesis Estructurada Local" in prov_o else "OK"
    print(f"[{tag_o}] Tool 5 S3 (prefer=ollama): proveedor real={prov_o}")

    _step(6, "Tool 6 (`notificar`) + Regla Fija 2: Canal Algedónico Directo S5 (>25%)")
    code_n5, notif_s5 = _http_json(
        f"{api_base}/tools/notificar",
        method="POST",
        payload={"report_payload": rep_s5["informe"]},
    )
    assert code_n5 == 200 and notif_s5.get("canal_destino") == "S5_ALGEDONICO", f"S5 falló: {notif_s5}"
    assert notif_s5.get("estado_aprobacion_humana") == "ALGEDONICO_DIRECTO_S5"
    print(
        f"[OK] Alerta S5 ID={notif_s5['id_alerta']} ({notif_s5['distrito']}): "
        f"canal={notif_s5['canal_destino']} | estado={notif_s5['estado_aprobacion_humana']}"
    )

    _step(7, "Tool 6 (`notificar`) + Regla Fija 3: Compuerta Humana HITL hacia S3 (/hitl/aprobar)")
    code_n3, notif_s3 = _http_json(
        f"{api_base}/tools/notificar",
        method="POST",
        payload={"report_payload": rep_s3["informe"]},
    )
    assert code_n3 == 200 and notif_s3.get("canal_destino") == "S3_CONTROL", f"S3 falló: {notif_s3}"
    assert notif_s3.get("estado_aprobacion_humana") == "PENDIENTE_APROBACION"
    assert notif_s3.get("publicado_en_canal_control_s3") is False
    alert_id_s3 = notif_s3["id_alerta"]
    print(
        f"[OK] Pre-aprobación S3 ID={alert_id_s3} ({notif_s3['distrito']}): "
        f"estado={notif_s3['estado_aprobacion_humana']} | publicado={notif_s3['publicado_en_canal_control_s3']}"
    )

    code_hitl, hitl_res = _http_json(
        f"{api_base}/hitl/aprobar/{alert_id_s3}",
        method="POST",
        payload={
            "approved": True,
            "approver_name": "Elvis Arboleda (Ensayo E2E Equipo 1 -> Equipo 2)",
        },
    )
    assert code_hitl == 200 and hitl_res.get("estado_aprobacion_humana") == "APROBADO_S3", f"HITL falló: {hitl_res}"
    assert hitl_res.get("publicado_en_canal_control_s3") is True
    print(
        f"[OK] Post-aprobación HITL ID={alert_id_s3}: estado={hitl_res['estado_aprobacion_humana']} | "
        f"publicado={hitl_res['publicado_en_canal_control_s3']}"
    )

    elapsed = time.perf_counter() - t0_total
    print(f"\n=== ENSAYO E2E COMPLETO EXITOSO EN {elapsed:.2f}s (Equipo 1 -> Equipo 2 {host}) ===")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Ensayo End-to-End en vivo SentinelNutri-HVC")
    parser.add_argument("--host", default=None, help="IP LAN o hostname del Equipo 2 (por defecto lee .env.equipo1)")
    args = parser.parse_args()
    host = args.host or _read_equipo2_ip_from_env()
    raise SystemExit(run_rehearsal(host))


if __name__ == "__main__":
    main()
