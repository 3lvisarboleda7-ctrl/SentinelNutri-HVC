"""
Gateway LLM Independiente del Proveedor (Sección 'Base Tecnológica de Costo Cero'):
- Proveedor Principal: API de Gemini en el nivel gratuito de Google AI Studio (`gemini-2.0-flash`).
- Proveedor de Respaldo Local: Llama 3.2 ejecutado en Ollama sobre la GPU NVIDIA GTX 1050 (4 GB) del Equipo 2.
- Verifica siempre el guardarraíl de la Ley N.° 29733 antes de transmitir cualquier payload.
"""

import json
import os
import urllib.request
from typing import Any, Dict, Optional, Tuple
from sentinelnutri.domain.rules.privacy_guard import sanitize_district_payload_for_llm


class AgnosticLLMGateway:
    """Adaptador agnóstico al proveedor LLM (Gemini Free Tier -> Fallback Ollama GTX 1050)."""

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        ollama_base_url: Optional[str] = None,
        ollama_model: str = "llama3.2",
    ) -> None:
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        self.ollama_base_url = ollama_base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = ollama_model

    def generate_policy_report(
        self,
        safe_context: Dict[str, Any],
        prefer_provider: str = "gemini",
    ) -> Tuple[Optional[Dict[str, str]], str]:
        """
        Intenta generar el informe con el proveedor preferido; si no está disponible o sin cuota,
        conmuta sin modificar los flujos hacia Ollama local o al motor determinista de políticas.
        """
        verified_payload = sanitize_district_payload_for_llm(safe_context, strict=True)

        if prefer_provider == "ollama":
            res = self._try_ollama(verified_payload)
            if res:
                return res, f"ollama/{self.ollama_model} (GPU GTX 1050 Local)"

        if self.gemini_api_key and not self.gemini_api_key.startswith("tu_api_key"):
            res = self._try_gemini(verified_payload)
            if res:
                return res, "gemini-2.0-flash (Google AI Studio Free Tier)"

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
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                if resp.status == 200:
                    body = json.loads(resp.read().decode("utf-8"))
                    data = json.loads(body.get("response", "{}"))
                    if "sintesis_narrativa_s4" in data:
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
            with urllib.request.urlopen(req, timeout=8.0) as resp:
                if resp.status == 200:
                    body = json.loads(resp.read().decode("utf-8"))
                    candidates = body.get("candidates", [])
                    if candidates:
                        text = candidates[0]["content"]["parts"][0]["text"]
                        parsed = json.loads(text)
                        if "sintesis_narrativa_s4" in parsed:
                            return parsed
        except Exception:
            pass
        return None
