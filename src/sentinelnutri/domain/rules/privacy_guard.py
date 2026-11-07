"""
Guardarraíl de Privacidad de Datos conforme a la Ley N.° 29733 (Ley de Protección de Datos Personales).

Garantiza por código que hacia los proveedores de LLM (Gemini API en Google AI Studio u Ollama)
solo se envíen indicadores agregados por distrito y jamás datos nominales o identificables de niños o madres.
"""

from typing import Any, Dict, Set

FORBIDDEN_NOMINAL_KEYS: Set[str] = {
    "dni",
    "cui",
    "num_doc",
    "documento_identidad",
    "nombre",
    "nombres",
    "apellido",
    "apellidos",
    "nombre_nino",
    "nombre_madre",
    "historia_clinica",
    "hc",
    "direccion",
    "domicilio",
    "telefono",
    "celular",
    "fecha_nacimiento_exacta",
    "coordenada_vivienda",
}


class PrivacyViolationError(ValueError):
    """Excepción lanzada cuando se intenta enviar datos personales/nominales a un LLM externo."""


def sanitize_district_payload_for_llm(
    payload: Dict[str, Any],
    strict: bool = True,
) -> Dict[str, Any]:
    """
    Verifica y filtra un diccionario de datos antes de enviarlo al LLM (Herramienta redactar_informe).
    - Si `strict=True`, lanza `PrivacyViolationError` ante cualquier campo nominal prohibido.
    - Si `strict=False`, elimina recursivamente cualquier clave prohibida.
    """
    sanitized: Dict[str, Any] = {}
    for key, value in payload.items():
        normalized_key = str(key).strip().lower()
        if normalized_key in FORBIDDEN_NOMINAL_KEYS:
            if strict:
                raise PrivacyViolationError(
                    f"Violación de Ley N.° 29733: El campo nominal '{key}' no puede enviarse al LLM. "
                    "Solo se permiten indicadores agregados por ubigeo distrital."
                )
            continue

        if isinstance(value, dict):
            sanitized[key] = sanitize_district_payload_for_llm(value, strict=strict)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_district_payload_for_llm(item, strict=strict)
                if isinstance(item, dict)
                else item
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized

