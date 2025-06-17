# src/config.py

import yaml
from pydantic import BaseModel, Field, validator
import logging
import os
from typing import Optional, List, Tuple
from src.constants import MetricType 

logger = logging.getLogger(__name__)

try:
    import mediapipe as mp
    PoseLandmark = mp.solutions.pose.PoseLandmark
except ImportError:
    PoseLandmark = None

# --- 1. Definición de la Estructura de la Configuración con Pydantic ---

# -- Modelos Anidados para una Estructura Limpia --

class AnalysisParams(BaseModel):
    use_3d_analysis: bool
    generate_debug_video: bool
    debug_mode: bool
    default_rotate: int

class MetricDefinition(BaseModel):
    name: str
    # --- CAMBIO: Usamos el Enum para el tipo, con 'angle' por defecto ---
    type: MetricType = MetricType.ANGLE 
    point_names: Optional[List[str]] = None
    point_name: Optional[str] = None

    # El validador ahora comprueba contra el Enum
    @validator('point_names', always=True)
    def validate_angle_points(cls, v, values):
        if values.get('type') == MetricType.ANGLE: # <-- Usamos el Enum
            if not v or len(v) != 3:
                raise ValueError("Métricas de tipo 'angle' deben tener 3 'point_names'.")
        return v

class SquatParams(BaseModel):
    metric_definitions: List[MetricDefinition]
    rep_counter_metric: str
    high_thresh: float
    low_thresh: float
    depth_fail_thresh: float
    peak_prominence: float
    peak_distance: int

    @validator('metric_definitions')
    def check_unique_metric_names(cls, v):
        names = [metric.name for metric in v]
        if len(names) != len(set(names)):
            raise ValueError("Los nombres en 'metric_definitions' deben ser únicos.")
        return v
        
    @validator('rep_counter_metric')
    def check_rep_counter_metric_exists(cls, v, values):
        if 'metric_definitions' in values:
            defined_names = {metric.name for metric in values['metric_definitions']}
            if v not in defined_names:
                raise ValueError(f"'{v}' no está definido en 'metric_definitions'.")
        return v

class PerformanceParams(BaseModel):
    max_workers: int
    preprocess_size: Optional[List[int]]

class PlotThemeParams(BaseModel):
    background_color: str
    axis_color: str
    line_color_left: str
    line_color_right: str
    vline_color: str
    line_thickness: int
    vline_thickness: int

class SkeletonThemeParams(BaseModel):
    line_color_bgr: Tuple[int, int, int]
    point_color_bgr: Tuple[int, int, int]
    thickness: int
    radius: int

class ThemeParams(BaseModel):
    plot: PlotThemeParams
    skeleton: SkeletonThemeParams

class DrawingConfig(BaseModel):
    light_theme: ThemeParams
    dark_theme: ThemeParams

# -- Modelo Principal de Configuración --
class AppConfig(BaseModel):
    analysis_params: AnalysisParams
    squat_params: SquatParams
    performance_params: PerformanceParams
    drawing: DrawingConfig # Renombrado para coincidir con el YAML


# --- 2. Función para Cargar la Configuración ---
def load_config(config_path: str = "config.yaml") -> AppConfig:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"El fichero de configuración '{config_path}' no se encontró. Asegúrate de que está en la raíz del proyecto.")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        config_model = AppConfig(**config_data)
        logger.info(f"Configuración cargada y validada correctamente desde '{config_path}'.")
        return config_model
    except Exception as e:
        logger.error(f"Error al cargar o validar la configuración desde '{config_path}': {e}", exc_info=True)
        raise


# --- 3. Objeto de Configuración Global ---
settings = load_config()