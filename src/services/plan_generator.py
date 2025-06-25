from __future__ import annotations

import asyncio
import logging
import os

from PyQt5.QtCore import QThread, pyqtSignal

# Se importa opcionalmente para no romper en entornos sin la librería
try:  # pragma: no cover - import protegido
    import google.generativeai as genai
except Exception:  # pragma: no cover - sin dependencia
    genai = None

logger = logging.getLogger(__name__)


async def generate_plan(objetivo: str, dias: int, nivel: str, enfoque: str) -> str:
    """Genera un plan de entrenamiento usando el modelo Gemini."""

    prompt = f"""
Actúa como un entrenador personal experto. 
Crea un plan de entrenamiento semanal detallado para un individuo con los siguientes parámetros:
- Objetivo principal: {objetivo}
- Días de entrenamiento por semana: {dias}
- Nivel de experiencia: {nivel}
- Enfoque muscular adicional: {enfoque if enfoque else 'Ninguno'}

Estructura la respuesta en formato Markdown. Para cada día de entrenamiento, lista los ejercicios, el número de series y el rango de repeticiones. Proporciona también una breve justificación de la estructura del plan.
"""

    if genai is None:
        raise RuntimeError("google-generativeai no está instalado")

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY no está configurada")

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = await model.generate_content_async(prompt)
        plan_text = getattr(response, "text", str(response))
        return plan_text.strip()
    except Exception as exc:  # pragma: no cover - llamada externa
        logger.exception("Error llamando a Gemini")
        raise RuntimeError(str(exc))


class PlanGeneratorWorker(QThread):
    """Ejecuta la generación de planes en segundo plano."""

    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, objetivo: str, dias: int, nivel: str, enfoque: str, parent=None) -> None:
        super().__init__(parent)
        self.objetivo = objetivo
        self.dias = dias
        self.nivel = nivel
        self.enfoque = enfoque

    def run(self) -> None:
        try:
            plan = asyncio.run(
                generate_plan(self.objetivo, self.dias, self.nivel, self.enfoque)
            )
            self.finished.emit(plan)
        except Exception as exc:  # pragma: no cover - ejecución en hilo
            self.error.emit(str(exc))
