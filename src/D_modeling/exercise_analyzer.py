# src/D_modeling/exercise_analyzer.py
"""
Módulo central y unificado para todo el análisis de ejercicios.
Contiene un motor de análisis genérico, robusto y optimizado.
"""
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import logging
from typing import List, Tuple, Dict, Any

from src.config import settings, SquatParams, MetricDefinition
from src.constants import MetricType
from src.B_pose_estimation.estimators import EstimationResult
from src.D_modeling.math_utils import calculate_angle_3d

try:
    import mediapipe as mp
    PoseLandmark = mp.solutions.pose.PoseLandmark
except ImportError:
    PoseLandmark = None

logger = logging.getLogger(__name__)


def calculate_metrics(
    estimation_results: List[EstimationResult], 
    fps: int, 
    metric_definitions: List[MetricDefinition]
) -> pd.DataFrame:
    """
    Motor de cálculo de métricas genérico, optimizado y robusto.
    Calcula solo las métricas especificadas en la lista de definiciones.

    Returns:
        pd.DataFrame: Un DataFrame con una fila por frame y columnas para
                      cada métrica calculada.
    """
    if not PoseLandmark:
        logger.error("MediaPipe no está disponible para calcular métricas.")
        return pd.DataFrame()

    # Optimización: Pre-inicializamos un diccionario de listas para un ensamblado rápido del DataFrame
    metric_columns = {metric.name: [] for metric in metric_definitions}
    base_columns = {'frame_idx': [], 'time_s': []}
    data = {**base_columns, **metric_columns}

    for frame_idx, result in enumerate(estimation_results):
        data['frame_idx'].append(frame_idx)
        data['time_s'].append(frame_idx / fps)
        
        source_landmarks = result.world_landmarks or result.landmarks
        
        # Mapa de Nombre -> Datos de Landmark para este frame
        landmarks_by_name = {}
        if source_landmarks:
            # Pre-filtramos por visibilidad para mayor robustez
            for i, lm in enumerate(source_landmarks):
                if lm['visibility'] > 0.5:
                    landmarks_by_name[PoseLandmark(i).name] = lm
        
        # Iteramos sobre las "recetas" de métricas de nuestra configuración
        for metric_def in metric_definitions:
            metric_name = metric_def.name
            metric_value = None # Valor por defecto si algo falla
            try:
                if metric_def.type == MetricType.ANGLE:
                    p1_name, p2_name, p3_name = metric_def.point_names
                    p1, p2, p3 = landmarks_by_name.get(p1_name), landmarks_by_name.get(p2_name), landmarks_by_name.get(p3_name)
                    if all([p1, p2, p3]):
                        metric_value = calculate_angle_3d(p1, p2, p3)
                
                elif metric_def.type == MetricType.HEIGHT:
                    point = landmarks_by_name.get(metric_def.point_name)
                    if point:
                        metric_value = point['y']
            except Exception as e:
                logger.error(f"Error calculando métrica '{metric_name}' en frame {frame_idx}: {e}")
            
            data[metric_name].append(metric_value)

    return pd.DataFrame.from_dict(data)


def count_repetitions(df_metrics: pd.DataFrame, params: SquatParams) -> int:
    """
    Wrapper unificado que cuenta repeticiones usando el robusto algoritmo de detección de picos.
    """
    angle_column = params.rep_counter_metric
    
    if df_metrics.empty or angle_column not in df_metrics.columns:
        logger.warning(f"No se puede contar repeticiones, falta la columna '{angle_column}'.")
        return 0

    angles = df_metrics[angle_column].ffill().bfill().to_numpy()
    if len(angles) == 0: return 0

    inverted_angles = -angles
    inverted_threshold = -params.low_thresh
    
    valleys, _ = find_peaks(
        inverted_angles, height=inverted_threshold, 
        prominence=params.peak_prominence, distance=params.peak_distance
    )
    
    logger.info(f"Detección de picos encontró {len(valleys)} repeticiones válidas usando '{angle_column}'.")
    return len(valleys)


def detect_faults(df_metrics: pd.DataFrame, rep_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Placeholder para la lógica de detección de fallos.
    """
    logger.info("La detección de fallos aún no está implementada.")
    return []