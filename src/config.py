# src/config.py

import yaml
from pydantic import BaseModel, Field, validator
import logging
import os
from typing import Optional, List, Tuple, Dict

from src.constants import MetricType

logger = logging.getLogger(__name__)

try:
    import mediapipe as mp
    PoseLandmark = mp.solutions.pose.PoseLandmark
except ImportError:
    PoseLandmark = None

# --- Modelos de Pydantic para validar config.yaml ---

class AnalysisParams(BaseModel):
    """Parámetros que controlan el tipo y el nivel de detalle del análisis."""
    use_3d_analysis: bool
    generate_debug_video: bool
    debug_mode: bool
    default_rotate: int

class MetricDefinition(BaseModel):
    """Define una única métrica, su tipo y los puntos necesarios."""
    name: str
    type: MetricType = MetricType.ANGLE
    point_names: Optional[List[str]] = None
    point_name: Optional[str] = None

    @validator('point_names', always=True)
    def validate_angle_points(cls, v, values):
        if values.get('type') == MetricType.ANGLE:
            if not v or len(v) != 3:
                raise ValueError("Métricas de tipo 'angle' deben tener una lista de 3 'point_names'.")
            if PoseLandmark and v:
                for point in v:
                    if point not in PoseLandmark.__members__:
                        raise ValueError(f"Landmark '{point}' no es un miembro válido de PoseLandmark.")
        return v

# Renombrado de SquatParams a ExerciseParams para admitir múltiples ejercicios
class ExerciseParams(BaseModel):
    """Parámetros específicos para un tipo de ejercicio."""
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
    """Parámetros para ajustar el rendimiento y el uso de recursos."""
    max_workers: int
    preprocess_size: Optional[List[int]]

class PlotThemeParams(BaseModel):
    """Define los colores y estilos para un tema del gráfico."""
    background_color: str
    axis_color: str
    line_color_left: str
    line_color_right: str
    vline_color: str
    line_thickness: int
    vline_thickness: int
    threshold_color: Optional[str] = None  # Color de las líneas de umbral, por defecto axis_color si no se especifica

    @validator('threshold_color', always=True)
    def set_default_threshold_color(cls, v, values):
        """Si no se proporciona threshold_color, usar axis_color como valor por defecto."""
        if v is None:
            axis = values.get('axis_color')
            if axis is None:
                raise ValueError("axis_color debe estar definido para asignar threshold_color por defecto")
            return axis
        return v

class SkeletonThemeParams(BaseModel):
    """Define los colores y estilos para el esqueleto dibujado en el vídeo."""
    line_color_bgr: Tuple[int, int, int]
    point_color_bgr: Tuple[int, int, int]
    thickness: int
    radius: int

class ThemeParams(BaseModel):
    """Agrupa los estilos de plot y skeleton para un tema."""
    plot: PlotThemeParams
    skeleton: SkeletonThemeParams

class DrawingConfig(BaseModel):
    """Contiene la configuración de estilo para ambos temas."""
    light_theme: ThemeParams
    dark_theme: ThemeParams

class AppConfig(BaseModel):
    """Modelo principal que contiene toda la configuración de la aplicación."""
    analysis_params: AnalysisParams
    # Diccionario de parámetros por ejercicio
    exercises: Dict[str, ExerciseParams]
    performance_params: PerformanceParams
    drawing: DrawingConfig


def load_config(config_path: str = "config.yaml") -> AppConfig:
    """Carga la configuración desde un fichero YAML y la valida con Pydantic."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"El fichero de configuración '{config_path}' no se encontró.")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        config_model = AppConfig(**config_data)
        logger.info(f"Configuración cargada y validada desde '{config_path}'.")
        return config_model
    except Exception as e:
        logger.error(f"Error al cargar o validar la configuración desde '{config_path}': {e}", exc_info=True)
        raise

# Objeto de configuración global que se importará en otros módulos.
settings = load_config()
