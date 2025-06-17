# src/D_modeling/exercise_analyzer.py
"""
Módulo central y unificado para todo el análisis de ejercicios.
Contiene un motor de análisis genérico que se configura desde config.yaml.
"""
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import logging
from typing import List, Tuple, Dict

from src.config import settings as global_settings
from src.B_pose_estimation.estimators import EstimationResult
from src.D_modeling.math_utils import calculate_angle_3d

try:
    import mediapipe as mp
    PoseLandmark = mp.solutions.pose.PoseLandmark
except ImportError:
    PoseLandmark = None

logger = logging.getLogger(__name__)


def calculate_metrics(estimation_results: List[EstimationResult], fps: int, metric_definitions: List) -> pd.DataFrame:
    """
    Motor de cálculo de métricas genérico.
    Lee las definiciones de métricas desde la configuración global y las calcula.
    """
    if not PoseLandmark:
        logger.error("MediaPipe no está disponible para calcular métricas.")
        return pd.DataFrame()

    processed_metrics = []
    
    for frame_idx, result in enumerate(estimation_results):
        frame_metrics = {'frame_idx': frame_idx, 'time_s': frame_idx / fps}
        
        # Priorizamos los landmarks 3D si están disponibles
        source_landmarks = result.world_landmarks if result.world_landmarks else result.landmarks
        
        if source_landmarks:
            # Creamos un mapa de Nombre -> Datos de Landmark para un acceso fácil y legible
            landmarks_by_name = {lm_name.name: source_landmarks[lm_name.value] for lm_name in PoseLandmark}
            
            # Iteramos sobre las métricas que nos han pedido calcular en config.yaml
            for metric_def in metric_definitions:
                metric_name = metric_def.name
                try:
                    # Lógica para calcular un ángulo
                    if metric_def.type == 'angle':
                        p1_name, p2_name, p3_name = metric_def.point_names
                        p1 = landmarks_by_name.get(p1_name)
                        p2 = landmarks_by_name.get(p2_name)
                        p3 = landmarks_by_name.get(p3_name)
                        
                        if all([p1, p2, p3]):
                            frame_metrics[metric_name] = calculate_angle_3d(p1, p2, p3)
                        else:
                            frame_metrics[metric_name] = None
                    
                    # Lógica para calcular una altura
                    elif metric_def.type == 'height':
                        point = landmarks_by_name.get(metric_def.point_name)
                        frame_metrics[metric_name] = point['y'] if point else None
                        
                except Exception as e:
                    logger.error(f"Error calculando la métrica '{metric_name}' en el frame {frame_idx}: {e}")
                    frame_metrics[metric_name] = None
        
        processed_metrics.append(frame_metrics)

    return pd.DataFrame(processed_metrics)


def count_repetitions(df_metrics: pd.DataFrame) -> int:
    """
    Wrapper unificado que cuenta repeticiones usando el robusto algoritmo de detección de valles.
    Ahora lee qué métrica usar desde la configuración.
    """
    # Leemos desde la config qué columna usar para contar las repeticiones
    angle_column = global_settings.squat_params.rep_counter_metric
    
    if df_metrics.empty or angle_column not in df_metrics.columns:
        logger.warning(f"No se puede contar repeticiones, falta la columna '{angle_column}'.")
        return 0

    angles = df_metrics[angle_column].ffill().bfill().tolist()
    if not angles: return 0

    # Usamos los parámetros del detector de picos desde la configuración
    inverted_angles = -np.array(angles)
    inverted_threshold = -global_settings.squat_params.low_thresh
    
    valleys, _ = find_peaks(
        inverted_angles, 
        height=inverted_threshold, 
        prominence=global_settings.squat_params.peak_prominence, 
        distance=global_settings.squat_params.peak_distance
    )
    
    logger.info(f"Detección de picos encontró {len(valleys)} repeticiones válidas usando '{angle_column}'.")
    return len(valleys)


def detect_faults(df_metrics: pd.DataFrame, rep_data: dict) -> List[dict]:
    """
    Placeholder para la lógica de detección de fallos.
    Aquí es donde se cargaría y usaría el modelo de Machine Learning.
    """
    logger.info("La detección de fallos (por reglas o por IA) aún no está implementada en esta versión.")
    faults = []
    return faults