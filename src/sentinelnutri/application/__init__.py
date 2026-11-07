"""
Capa de Aplicación: Implementa las 6 Herramientas del Agente Supervisor (Tabla 5 del Proyecto).

1. extraer_fuentes  (Tool1ExtraerFuentesUseCase)
2. consultar_bd     (Tool2ConsultarBdUseCase)
3. predecir_riesgo  (Tool3PredecirRiesgoUseCase)
4. explicar_riesgo  (Tool4ExplicarRiesgoUseCase)
5. redactar_informe (Tool5RedactarInformeUseCase)
6. notificar        (Tool6NotificarUseCase)
"""

from .tool_1_extraer_fuentes import Tool1ExtraerFuentesUseCase
from .tool_2_consultar_bd import Tool2ConsultarBdUseCase
from .tool_3_predecir_riesgo import Tool3PredecirRiesgoUseCase
from .tool_4_explicar_riesgo import Tool4ExplicarRiesgoUseCase
from .tool_5_redactar_informe import Tool5RedactarInformeUseCase
from .tool_6_notificar import Tool6NotificarUseCase

__all__ = [
    "Tool1ExtraerFuentesUseCase",
    "Tool2ConsultarBdUseCase",
    "Tool3PredecirRiesgoUseCase",
    "Tool4ExplicarRiesgoUseCase",
    "Tool5RedactarInformeUseCase",
    "Tool6NotificarUseCase",
]

