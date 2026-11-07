"""
Pruebas Unitarias del Guardarraíl de Privacidad de Datos (Ley N.° 29733):
Verifica que jamás puedan enviarse datos nominales (DNI, nombres, historia clínica, dirección)
hacia la API externa de Gemini ni a ningún otro LLM; únicamente indicadores agregados por distrito.
"""

from sentinelnutri.domain.rules.privacy_guard import (
    PrivacyViolationError,
    sanitize_district_payload_for_llm,
)


def test_strict_privacy_guard_rejects_nominal_fields() -> None:
    contaminated_payload = {
        "ubigeo": "090101",
        "distrito": "Huancavelica",
        "dci_proyectada_pct": 21.4,
        "dni": "45678912",
        "nombre_nino": "Juan Perez",
    }
    raised = False
    try:
        sanitize_district_payload_for_llm(contaminated_payload, strict=True)
    except PrivacyViolationError as exc:
        raised = "Ley N.° 29733" in str(exc)
    assert raised is True


def test_non_strict_privacy_guard_strips_nominal_fields_cleanly() -> None:
    raw_diresa_row = {
        "ubigeo": "090206",
        "distrito": "Paucará",
        "historia_clinica": "HC-9981",
        "nombres": "Maria",
        "tasa_dci_pct": 28.5,
    }
    cleaned = sanitize_district_payload_for_llm(raw_diresa_row, strict=False)
    assert "historia_clinica" not in cleaned
    assert "nombres" not in cleaned
    assert cleaned["ubigeo"] == "090206"
    assert cleaned["tasa_dci_pct"] == 28.5
