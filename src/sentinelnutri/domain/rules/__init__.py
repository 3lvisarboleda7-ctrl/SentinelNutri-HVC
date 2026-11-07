"""Reglas Fijas Cibernéticas, Privacidad Ley N.° 29733 y Ética de Extracción."""

from .fixed_thresholds import (
    ALGEDONIC_DCI_THRESHOLD_PCT,
    AlgedonicRouteDecision,
    classify_risk_level,
    can_publish_to_s3_control,
    evaluate_fixed_algedonic_rule,
)
from .privacy_guard import PrivacyViolationError, sanitize_district_payload_for_llm
from .scraping_ethics import (
    DEFAULT_ACADEMIC_USER_AGENT,
    compute_sha256_hash,
    has_file_changed,
    is_url_allowed_by_robots,
    validate_academic_user_agent,
)

__all__ = [
    "ALGEDONIC_DCI_THRESHOLD_PCT",
    "AlgedonicRouteDecision",
    "classify_risk_level",
    "evaluate_fixed_algedonic_rule",
    "can_publish_to_s3_control",
    "PrivacyViolationError",
    "sanitize_district_payload_for_llm",
    "DEFAULT_ACADEMIC_USER_AGENT",
    "compute_sha256_hash",
    "has_file_changed",
    "is_url_allowed_by_robots",
    "validate_academic_user_agent",
]

