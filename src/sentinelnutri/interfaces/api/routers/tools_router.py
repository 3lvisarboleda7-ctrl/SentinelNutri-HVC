"""Router informativo del catálogo de las 6 Herramientas del Agente Supervisor (Tabla 5)."""

from typing import Dict, List
from fastapi import APIRouter

router = APIRouter(tags=["Herramientas del Agente Supervisor (Tabla 5)"])


@router.get("/tools/catalog")
def list_supervisor_agent_tools() -> List[Dict[str, str]]:
    return [
        {
            "herramienta": "extraer_fuentes",
            "endpoint": "POST /tools/extraer_fuentes",
            "que_hace": "Revisa los portales, detecta publicaciones nuevas y las descarga",
            "componente": "n8n + FastAPI / Playwright",
        },
        {
            "herramienta": "consultar_bd",
            "endpoint": "GET /tools/consultar_bd",
            "que_hace": "Lee las series históricas por distrito y el registro de cargas",
            "componente": "PostgreSQL",
        },
        {
            "herramienta": "predecir_riesgo",
            "endpoint": "POST /predict",
            "que_hace": "Calcula el índice de riesgo de DCI por distrito",
            "componente": "CatBoost (API /predict)",
        },
        {
            "herramienta": "explicar_riesgo",
            "endpoint": "GET /tools/explicar_riesgo/{ubigeo}",
            "que_hace": "Identifica las variables que explican el riesgo de cada distrito",
            "componente": "SHAP",
        },
        {
            "herramienta": "redactar_informe",
            "endpoint": "POST /tools/redactar_informe",
            "que_hace": "Elabora la síntesis narrativa y las recomendaciones por provincia y sector",
            "componente": "LLM (Gemini u Ollama)",
        },
        {
            "herramienta": "notificar",
            "endpoint": "POST /tools/notificar",
            "que_hace": "Publica en el dashboard y envía las alertas",
            "componente": "Streamlit, Telegram y Gmail",
        },
    ]

