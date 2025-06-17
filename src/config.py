# src/config.py

import yaml
from pydantic import BaseModel, Field, validator
import logging
import os
from typing import Optional, List, Tuple, Dict

logger = logging.getLogger(__name__)

try:
    import mediapipe as mp
    PoseLandmark = mp.solutions.pose.PoseLandmark
except ImportError:
    PoseLandmark = None

# --- Modelos de Pydantic ---

class AnalysisParams(BaseModel):
    use_3d_analysis: bool = Field(True)
    generate_debug_video: bool = Field(True)
    debug_mode: bool = Field(False)

class PerformanceParams(BaseModel):
    max_workers: int = Field(0)
    preprocess_size: Optional[List[int]] = Field([480, 854])
    
class DrawingParams(BaseModel):
    line_color_bgr: Tuple[int, int, int] = Field((0, 255, 0))
    point_color_bgr: Tuple[int, int, int] = Field((0, 0, 255))
    line_thickness: int = Field(2)
    point_radius: int = Field(5)

class MetricDefinition(BaseModel):
    name: str; type: str = 'angle'
    point_names: Optional[List[str]] = None
    point_name: Optional[str] = None
    @validator('point_names', always=True)
    def validate_angle_points(cls, v, values):
        if values.get('type') == 'angle':
            if not v or len(v) != 3: raise ValueError("Métricas 'angle' deben tener 3 'point_names'.")
            if PoseLandmark:
                for point in v:
                    if point not in PoseLandmark.__members__: raise ValueError(f"'{point}' no es un PoseLandmark válido.")
        return v

class SquatParams(BaseModel):
    metric_definitions: List[MetricDefinition]
    rep_counter_metric: str
    high_thresh: float
    low_thresh: float
    depth_fail_thresh: float
    peak_prominence: float
    peak_distance: int

    # --- VALIDADOR AVANZADO AÑADIDO ---
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
                raise ValueError(f"'{v}' no es un nombre de métrica válido definido en 'metric_definitions'.")
        return v

class AppConfig(BaseModel):
    analysis_params: AnalysisParams
    squat_params: SquatParams
    performance_params: PerformanceParams
    drawing_params: DrawingParams

# --- Función de Carga  ---
def load_config(config_path: str = "config.yaml") -> AppConfig:
    if not os.path.exists(config_path): raise FileNotFoundError(f"'{config_path}' no encontrado.")
    try:
        with open(config_path, 'r', encoding='utf-8') as f: config_data = yaml.safe_load(f)
        config_model = AppConfig(**config_data)
        logger.info(f"Configuración cargada y validada desde '{config_path}'.")
        return config_model
    except Exception as e:
        logger.error(f"Error al cargar o validar la configuración desde '{config_path}': {e}", exc_info=True)
        raise

settings = load_config()