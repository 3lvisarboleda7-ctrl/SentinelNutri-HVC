"""
Reglas de Extracción Automatizada Responsable (Sección 'Fuentes de Datos y Extracción Automatizada').

1. Respeta el archivo robots.txt de cada portal público.
2. Identifica al cliente como proyecto académico de la FIIS-UNI.
3. Calcula la huella digital (hash SHA-256) de cada archivo para procesar únicamente lo que cambió.
"""

import hashlib
from urllib.robotparser import RobotFileParser

DEFAULT_ACADEMIC_USER_AGENT: str = (
    "SentinelNutri-HVC/1.0 (Proyecto Academico FIIS-UNI; MSV-S4; mailto:elvis.arboleda@uni.pe)"
)


def compute_sha256_hash(content: bytes) -> str:
    """Calcula la huella digital SHA-256 en formato hexadecimal de un archivo o respuesta HTTP."""
    return hashlib.sha256(content).hexdigest()


def has_file_changed(new_content: bytes, previous_hash_sha256: str | None) -> bool:
    """Compara la huella digital del archivo descargado con el último registro en PostgreSQL."""
    if not previous_hash_sha256:
        return True
    current_hash = compute_sha256_hash(new_content)
    return current_hash.lower() != previous_hash_sha256.strip().lower()


def is_url_allowed_by_robots(
    robots_txt_content: str,
    target_url: str,
    user_agent: str = DEFAULT_ACADEMIC_USER_AGENT,
) -> bool:
    """Evalúa si la URL objetivo está permitida según el contenido del archivo robots.txt del portal."""
    parser = RobotFileParser()
    parser.parse(robots_txt_content.splitlines())
    return parser.can_fetch(user_agent, target_url)


def validate_academic_user_agent(user_agent: str) -> bool:
    """Verifica que el User-Agent identifique explícitamente al proyecto académico."""
    ua_lower = user_agent.lower()
    return "sentinelnutri-hvc" in ua_lower and ("academico" in ua_lower or "uni" in ua_lower)

