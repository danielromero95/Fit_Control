# Contenido completo y correcto para: src/config.py

import yaml
from pydantic import BaseModel, Field
import logging
import os

logger = logging.getLogger(__name__)

# --- 1. Definición de la Estructura de la Configuración con Pydantic ---
class AnalysisParams(BaseModel):
    use_3d_analysis: bool = Field(True, description="Activa el pipeline de análisis 3D.")
    generate_debug_video: bool = Field(True, description="Genera un vídeo con los landmarks.")
    debug_mode: bool = Field(False, description="Guarda ficheros intermedios de datos.")

class SquatParams(BaseModel):
    high_thresh: float = Field(160.0, description="Umbral de ángulo para la posición 'arriba'.")
    low_thresh: float = Field(100.0, description="Umbral de ángulo para la posición 'abajo'.")
    depth_fail_thresh: float = Field(90.0, description="Umbral para el fallo de profundidad.")
    
    peak_prominence: float = Field(10.0, description="Prominencia para el detector de picos.")
    peak_distance: int = Field(15, description="Distancia mínima en frames entre repeticiones.")

class AppConfig(BaseModel):
    """Modelo principal que contiene toda la configuración de la aplicación."""
    analysis_params: AnalysisParams
    squat_params: SquatParams


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
        
        config = AppConfig(**config_data)
        logger.info(f"Configuración cargada y validada correctamente desde '{config_path}'.")
        return config
    except Exception as e:
        logger.error(f"Error al cargar o validar la configuración desde '{config_path}': {e}")
        raise

# --- 3. Objeto de Configuración Global que se importará en otros módulos ---
settings = load_config()