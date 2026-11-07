"""Entidades del Dominio de SentinelNutri-HVC."""

from .district import DistrictIndicatorRecord, DistrictMetadata
from .prediction import DistrictRiskPrediction, RiskLevel, ShapContribution
from .alert_msv import ApprovalStatus, MSVAlertReport, MSVChannel

__all__ = [
    "DistrictMetadata",
    "DistrictIndicatorRecord",
    "RiskLevel",
    "ShapContribution",
    "DistrictRiskPrediction",
    "MSVChannel",
    "ApprovalStatus",
    "MSVAlertReport",
]

