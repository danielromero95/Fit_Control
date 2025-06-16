# src/config.py

import yaml
from pydantic import BaseModel, Field
import logging
import os
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)

# --- 1. Definición de la Estructura de la Configuración con Pydantic ---

class AnalysisParams(BaseModel):
    """Parámetros que controlan el tipo y el nivel de detalle del análisis."""
    use_3d_analysis: bool = Field(True, description="Activa el pipeline de análisis 3D.")
    generate_debug_video: bool = Field(True, description="Genera un vídeo con los landmarks.")
    debug_mode: bool = Field(False, description="Guarda ficheros intermedios de datos.")

class SquatParams(BaseModel):
    """Parámetros específicos para el análisis del ejercicio de sentadilla."""
    high_thresh: float = Field(160.0, description="Umbral de ángulo para la posición 'arriba'.")
    low_thresh: float = Field(100.0, description="Umbral de ángulo para la posición 'abajo'.")
    depth_fail_thresh: float = Field(90.0, description="Umbral para el fallo de profundidad.")
    peak_prominence: float = Field(10.0, description="Prominencia para el detector de picos.")
    peak_distance: int = Field(15, description="Distancia mínima en frames entre repeticiones.")

class PerformanceParams(BaseModel):
    """Parámetros para ajustar el rendimiento y el uso de recursos."""
    max_workers: int = Field(0, description="Procesos paralelos. 0 o -1 usa todos los núcleos disponibles menos uno.")
    preprocess_size: Optional[List[int]] = Field([480, 854], description="Tamaño (ancho, alto) para pre-redimensionar frames. Poner en null para no redimensionar.")

class DrawingParams(BaseModel):
    line_color_bgr: Tuple[int, int, int] = Field((0, 255, 0), description="Color BGR para las líneas del esqueleto.")
    point_color_bgr: Tuple[int, int, int] = Field((0, 0, 255), description="Color BGR para los puntos/landmarks.")
    line_thickness: int = Field(2, description="Grosor de las líneas del esqueleto.")
    point_radius: int = Field(5, description="Radio de los puntos/landmarks.")

class AppConfig(BaseModel):
    """Modelo principal que contiene toda la configuración de la aplicación."""
    analysis_params: AnalysisParams
    squat_params: SquatParams
    performance_params: PerformanceParams
    drawing_params: DrawingParams


# --- 2. Función para Cargar la Configuración ---

def load_config(config_path: str = "config.yaml") -> AppConfig:
    """
    Carga la configuración desde un fichero YAML y la valida con Pydantic.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"El fichero de configuración '{config_path}' no se encontró. Asegúrate de que está en la raíz del proyecto.")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        config_model = AppConfig(**config_data)
        logger.info(f"Configuración cargada y validada correctamente desde '{config_path}'.")
        return config_model
    except Exception as e:
        logger.error(f"Error al cargar o validar la configuración desde '{config_path}': {e}")
        raise

# --- 3. Objeto de Configuración Global que se importará en otros módulos ---
settings = load_config()