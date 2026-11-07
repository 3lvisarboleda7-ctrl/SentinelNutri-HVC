"""Módulo de configuración y detección automática de nodo (Equipo 1 vs Equipo 2)."""

from .node_detector import NodeIdentity, detect_current_node

__all__ = ["NodeIdentity", "detect_current_node"]
