"""
Guardarraíl de Privacidad de Datos conforme a la Ley N.° 29733 (Ley de Protección de Datos Personales).

Garantiza por código que hacia los proveedores de LLM (Gemini API en Google AI Studio u Ollama)
solo se envíen indicadores agregados por distrito y jamás datos nominales o identificables de niños o madres.
Blindado contra estructuras profundamente anidadas (listas/tuplas de dicts), variantes compuestas de claves
y filtración de DNI en texto libre.
"""

import re
import unicodedata
from typing import Any, Dict, Set, Tuple

FORBIDDEN_NOMINAL_KEYS: Set[str] = {
    "dni",
    "cui",
    "num_doc",
    "nro_doc",
    "documento_identidad",
    "doc_identidad",
    "nombre",
    "nombres",
    "apellido",
    "apellidos",
    "nombre_nino",
    "nombre_menor",
    "nombre_madre",
    "nombre_paciente",
    "nombre_completo",
    "historia_clinica",
    "num_historia_clinica",
    "nro_historia_clinica",
    "hc",
    "direccion",
    "domicilio",
    "telefono",
    "telefono_celular",
    "celular",
    "fecha_nacimiento_exacta",
    "fecha_nacimiento",
    "coordenada_vivienda",
    "coordenadas_vivienda",
    "correo",
    "correo_electronico",
    "email",
}

FORBIDDEN_KEY_TOKENS: Set[str] = {
    "dni",
    "cui",
    "nombre",
    "nombres",
    "apellido",
    "apellidos",
    "hc",
    "direccion",
    "domicilio",
    "telefono",
    "celular",
    "correo",
    "email",
    "paciente",
    "apoderado",
}

FORBIDDEN_KEY_SUBSTRINGS: Tuple[str, ...] = (
    "historia_clinica",
    "num_historia",
    "nro_historia",
    "documento_identidad",
    "doc_identidad",
    "num_doc",
    "nro_doc",
    "fecha_nacimiento",
    "coordenada_vivienda",
    "coordenadas_vivienda",
    "coordenada_gps",
)

SAFE_NOMINAL_EXCEPTIONS: Set[str] = {
    "nombre_distrito",
    "nombre_provincia",
    "nombre_variable",
    "nombre_fuente",
    "nombre_indicador",
    "nombre_red_salud",
}

_EMBEDDED_DNI_REGEX = re.compile(r"(?i)\bdni\s*[:=#-]?\s*\d{8}\b")


class PrivacyViolationError(ValueError):
    """Excepción lanzada cuando se intenta enviar datos personales/nominales a un LLM externo."""


def _normalize_key(raw_key: Any) -> str:
    text = str(raw_key).strip().lower()
    decomposed = unicodedata.normalize("NFKD", text)
    without_accents = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return re.sub(r"[\s\-\.]+", "_", without_accents)


def _is_forbidden_nominal_key(raw_key: Any) -> bool:
    norm_key = _normalize_key(raw_key)
    if norm_key in SAFE_NOMINAL_EXCEPTIONS:
        return False
    if norm_key in FORBIDDEN_NOMINAL_KEYS:
        return True
    if any(sub in norm_key for sub in FORBIDDEN_KEY_SUBSTRINGS):
        return True
    tokens = [tok for tok in re.split(r"[^a-z0-9]+", norm_key) if tok]
    return any(tok in FORBIDDEN_KEY_TOKENS for tok in tokens)


def _sanitize_value(value: Any, strict: bool) -> Any:
    if isinstance(value, dict):
        return sanitize_district_payload_for_llm(value, strict=strict)
    if isinstance(value, list):
        return [_sanitize_value(item, strict=strict) for item in value]
    if isinstance(value, tuple):
        return tuple(_sanitize_value(item, strict=strict) for item in value)
    if isinstance(value, set):
        return {_sanitize_value(item, strict=strict) for item in value}
    if isinstance(value, str) and _EMBEDDED_DNI_REGEX.search(value):
        if strict:
            raise PrivacyViolationError(
                "Violación de Ley N.° 29733: Se detectó un número de DNI infiltrado en un campo de texto libre."
            )
        return _EMBEDDED_DNI_REGEX.sub("[DNI_PROTEGIDO_LEY_29733]", value)
    return value


def sanitize_district_payload_for_llm(
    payload: Dict[str, Any],
    strict: bool = True,
) -> Dict[str, Any]:
    """
    Verifica y filtra recursivamente un diccionario de datos antes de enviarlo al LLM (Herramienta redactar_informe).
    - Si `strict=True`, lanza `PrivacyViolationError` ante cualquier campo nominal prohibido o DNI infiltrado.
    - Si `strict=False`, elimina recursivamente cualquier clave prohibida y redacta DNIs en texto libre.
    """
    if not isinstance(payload, dict):
        raise TypeError("El payload a sanitizar para el LLM debe ser un diccionario.")

    sanitized: Dict[str, Any] = {}
    for key, value in payload.items():
        if _is_forbidden_nominal_key(key):
            if strict:
                raise PrivacyViolationError(
                    f"Violación de Ley N.° 29733: El campo nominal '{key}' no puede enviarse al LLM. "
                    "Solo se permiten indicadores agregados por ubigeo distrital."
                )
            continue

        sanitized[key] = _sanitize_value(value, strict=strict)

    return sanitized


