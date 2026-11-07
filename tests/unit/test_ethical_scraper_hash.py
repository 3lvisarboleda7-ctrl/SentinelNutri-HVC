"""
Pruebas Unitarias de Extracción Responsable (`scraping_ethics.py`):
1. Cálculo y comparación de huella digital SHA-256 para procesar únicamente archivos nuevos/modificados.
2. Verificación de cumplimiento del archivo `robots.txt` de cada portal público.
3. Identificación obligatoria del cliente como proyecto académico FIIS-UNI.
"""

from sentinelnutri.domain.rules.scraping_ethics import (
    DEFAULT_ACADEMIC_USER_AGENT,
    compute_sha256_hash,
    has_file_changed,
    is_url_allowed_by_robots,
    validate_academic_user_agent,
)


def test_sha256_hash_change_detection() -> None:
    payload_v1 = b"ubigeo,anio,dci\n090101,2024,20.3\n"
    payload_v2 = b"ubigeo,anio,dci\n090101,2025,19.8\n"

    hash_v1 = compute_sha256_hash(payload_v1)
    assert has_file_changed(payload_v1, None) is True
    assert has_file_changed(payload_v1, hash_v1) is False
    assert has_file_changed(payload_v2, hash_v1) is True


def test_robots_txt_compliance() -> None:
    sample_robots = """
User-agent: *
Disallow: /admin/
Allow: /publicaciones/
"""
    assert is_url_allowed_by_robots(sample_robots, "https://web.ins.gob.pe/publicaciones/sien.pdf") is True
    assert is_url_allowed_by_robots(sample_robots, "https://web.ins.gob.pe/admin/private.pdf") is False


def test_academic_user_agent_validation() -> None:
    assert validate_academic_user_agent(DEFAULT_ACADEMIC_USER_AGENT) is True
    assert validate_academic_user_agent("Mozilla/5.0 GenericBot") is False

