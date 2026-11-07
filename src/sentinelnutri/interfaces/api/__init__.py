"""Microservicio FastAPI que expone `/predict` y las 6 Herramientas del Agente Supervisor."""

from .main import app, create_app

__all__ = ["app", "create_app"]

