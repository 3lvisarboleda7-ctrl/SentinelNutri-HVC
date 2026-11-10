"""
Gateway LLM Independiente del Proveedor (Sección 'Base Tecnológica de Costo Cero'):
- Proveedor Principal (Ruta A): API de Gemini en el nivel gratuito de Google AI Studio (`gemini-2.0-flash`).
- Proveedor de Respaldo Local (Ruta B): Llama 3.2 ejecutado en Ollama sobre la GPU NVIDIA GTX 1050 (4 GB) del Equipo 2.
- Respaldo Determinista MSV (Ruta C): Plantilla cibernética estructurada (PEI 2020-2027 / ODS 2, 3, 6) que
  garantiza continuidad operativa 100 % y que jamás se bloquee el Canal Algedónico S5.
- Verifica siempre el guardarraíl de la Ley N.° 29733 antes de transmitir cualquier payload.
"""

import json
import os
import urllib.request
from typing import Any, Dict, Optional, Tuple
from sentinelnutri.domain.rules.privacy_guard import sanitize_district_payload_for_llm

REQUIRED_REPORT_KEYS: Tuple[str, ...] = (
    "sintesis_narrativa_s4",
    "recomendacion_salud",
    "recomendacion_agua_saneamiento",
    "recomendacion_agricultura_midis",
)


def is_valid_llm_policy_response(data: Any) -> bool:
    """Verifica que la respuesta JSON del LLM contenga las 4 claves obligatorias con texto no vacío."""
    if not isinstance(data, dict):
        return False
    return all(isinstance(data.get(k), str) and len(data[k].strip()) > 0 for k in REQUIRED_REPORT_KEYS)


class AgnosticLLMGateway:
    """Adaptador agnóstico al proveedor LLM (Ruta A: Gemini -> Ruta B: Ollama GTX 1050 -> Ruta C: Determinista)."""

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        ollama_base_url: Optional[str] = None,
        ollama_model: str = "llama3.2",
        gemini_timeout_sec: float = 4.0,
        ollama_timeout_sec: float = 1.5,
        attempt_ollama_when_unconfigured: bool = False,
    ) -> None:
        self.gemini_api_key = gemini_api_key if gemini_api_key is not None else os.getenv("GEMINI_API_KEY", "")
        raw_ollama_url = ollama_base_url if ollama_base_url is not None else os.getenv("OLLAMA_BASE_URL", "")
        self.ollama_base_url = raw_ollama_url or "http://localhost:11434"
        self._ollama_explicitly_configured = bool(raw_ollama_url) or attempt_ollama_when_unconfigured
        self.ollama_model = ollama_model
        self.gemini_timeout_sec = float(gemini_timeout_sec)
        self.ollama_timeout_sec = float(ollama_timeout_sec)

    def _has_valid_gemini_key(self) -> bool:
        return bool(self.gemini_api_key and not self.gemini_api_key.startswith("tu_api_key"))

    def generate_policy_report(
        self,
        safe_context: Dict[str, Any],
        prefer_provider: str = "gemini",
    ) -> Tuple[Optional[Dict[str, str]], str]:
        """
        Cadena de conmutación por fallo (Failover de 3 niveles):
        - Si `prefer_provider == "gemini"`: Ruta A (Gemini) -> Ruta B (Ollama GTX 1050) -> Ruta C (Determinista MSV).
        - Si `prefer_provider == "ollama"`: Ruta B (Ollama GTX 1050) -> Ruta A (Gemini) -> Ruta C (Determinista MSV).
        """
        verified_payload = sanitize_district_payload_for_llm(safe_context, strict=True)

        if prefer_provider == "ollama":
            res_b = self._try_ollama(verified_payload)
            if res_b:
                return res_b, f"ollama/{self.ollama_model} (GPU GTX 1050 Local)"
            if self._has_valid_gemini_key():
                res_a = self._try_gemini(verified_payload)
                if res_a:
                    return res_a, "gemini-2.0-flash (Google AI Studio Free Tier - Failover)"
        else:
            if self._has_valid_gemini_key():
                res_a = self._try_gemini(verified_payload)
                if res_a:
                    return res_a, "gemini-2.0-flash (Google AI Studio Free Tier)"
            if self._ollama_explicitly_configured or self._has_valid_gemini_key():
                res_b = self._try_ollama(verified_payload)
                if res_b:
                    return res_b, f"ollama/{self.ollama_model} (GPU GTX 1050 Local - Failover)"

        return None, "gemini-2.0-flash / ollama-llama3.2 (Síntesis Estructurada Local)"

    def _try_ollama(self, payload: Dict[str, Any]) -> Optional[Dict[str, str]]:
        try:
            prompt = (
                "Eres el Agente del Sistema 4 (Inteligencia) del GORE Huancavelica. "
                "Genera un JSON con las claves 'sintesis_narrativa_s4', 'recomendacion_salud', "
                "'recomendacion_agua_saneamiento' y 'recomendacion_agricultura_midis' para estos datos agregados: "
                + json.dumps(payload, ensure_ascii=False)
            )
            req_body = json.dumps(
                {"model": self.ollama_model, "prompt": prompt, "stream": False, "format": "json"}
            ).encode("utf-8")
            req = urllib.request.Request(
                f"{self.ollama_base_url.rstrip('/')}/api/generate",
                data=req_body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.ollama_timeout_sec) as resp:
                if resp.status == 200:
                    body = json.loads(resp.read().decode("utf-8"))
                    data = json.loads(body.get("response", "{}"))
                    if is_valid_llm_policy_response(data):
                        return data
        except Exception:
            pass
        return None

    def _try_gemini(self, payload: Dict[str, Any]) -> Optional[Dict[str, str]]:
        try:
            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"gemini-2.0-flash:generateContent?key={self.gemini_api_key}"
            )
            prompt = (
                "Actúa como el Sistema 4 (Inteligencia) del MSV del GORE Huancavelica. "
                "Devuelve exclusivamente un objeto JSON con las claves: "
                "sintesis_narrativa_s4, recomendacion_salud, recomendacion_agua_saneamiento, "
                "recomendacion_agricultura_midis. Datos agregados del distrito: "
                + json.dumps(payload, ensure_ascii=False)
            )
            req_body = json.dumps(
                {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json"},
                }
            ).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=req_body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.gemini_timeout_sec) as resp:
                if resp.status == 200:
                    body = json.loads(resp.read().decode("utf-8"))
                    candidates = body.get("candidates", [])
                    if candidates:
                        text = candidates[0]["content"]["parts"][0]["text"]
                        parsed = json.loads(text)
                        if is_valid_llm_policy_response(parsed):
                            return parsed
        except Exception:
            pass
        return None

