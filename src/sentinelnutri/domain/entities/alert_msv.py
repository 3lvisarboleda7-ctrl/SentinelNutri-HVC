"""Entidades de Alertas, Recomendaciones Sectoriales y Canales del MSV (S3 y S5)."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MSVChannel(str, Enum):
    """Canales cibernéticos del Modelo de Sistema Viable en el GORE Huancavelica."""

    S3_CONTROL = "S3_CONTROL"          # Gerencia Regional de Desarrollo Social (requiere HITL)
    S5_ALGEDONICO = "S5_ALGEDONICO"    # Consejo Regional / Gobernación (directo si DCI > 25%)


class ApprovalStatus(str, Enum):
    """Estados del protocolo de aprobación humana (HITL) según guía CEPAL (Clavijo, 2026)."""

    PENDIENTE_APROBACION = "PENDIENTE_APROBACION"
    APROBADO_S3 = "APROBADO_S3"
    ALGEDONICO_DIRECTO_S5 = "ALGEDONICO_DIRECTO_S5"
    RECHAZADO = "RECHAZADO"


@dataclass
class MSVAlertReport:
    """Informe generado por el Amplificador de Variedad (Agente Supervisor n8n + LLM)."""

    ubigeo: str
    provincia: str
    distrito: str
    nivel_riesgo: str
    dci_proyectada_pct: float
    canal_destino: MSVChannel
    sintesis_narrativa_s4: str
    recomendacion_salud: str
    recomendacion_agua_saneamiento: str
    recomendacion_agricultura_midis: str
    oei_pei_vinculados: str
    ods_vinculados: str
    proveedor_llm: str
    estado_aprobacion_humana: ApprovalStatus = ApprovalStatus.PENDIENTE_APROBACION
    aprobado_por: Optional[str] = None
    id_alerta: Optional[int] = None

