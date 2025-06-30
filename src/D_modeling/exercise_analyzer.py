# src/D_modeling/exercise_analyzer.py
"""
Módulo central y unificado para todo el análisis de ejercicios.
Contiene un motor de análisis genérico, robusto y optimizado.
"""
import pandas as pd
from scipy.signal import find_peaks
import logging
from typing import List, Dict, Any

from src.config import ExerciseParams, MetricDefinition
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

    # Preparamos las estructuras de salida y convertimos los nombres de landmark
    # a índices para evitar búsquedas costosas dentro del bucle principal
    name_to_idx = {lm.name: lm.value for lm in PoseLandmark}

    metric_rules = []  # (tipo, nombre_columna, indices)
    for metric in metric_definitions:
        if metric.type == MetricType.ANGLE:
            idxs = [name_to_idx[n] for n in metric.point_names]
            metric_rules.append((MetricType.ANGLE, metric.name, idxs))
        elif metric.type == MetricType.HEIGHT:
            idx = name_to_idx[metric.point_name]
            metric_rules.append((MetricType.HEIGHT, metric.name, [idx]))

    base_columns = {'frame_idx': [], 'time_s': []}
    metric_columns = {name: [] for _, name, _ in metric_rules}
    data = {**base_columns, **metric_columns}

    for frame_idx, result in enumerate(estimation_results):
        data['frame_idx'].append(frame_idx)
        data['time_s'].append(frame_idx / fps)

        source_landmarks = result.world_landmarks or result.landmarks
        if source_landmarks:
            visible_landmarks = [lm if lm['visibility'] > 0.5 else None for lm in source_landmarks]
        else:
            visible_landmarks = []

        for rule_type, metric_name, idxs in metric_rules:
            metric_value = None
            try:
                if all(i < len(visible_landmarks) and visible_landmarks[i] is not None for i in idxs):
                    if rule_type == MetricType.ANGLE:
                        p1, p2, p3 = (visible_landmarks[i] for i in idxs)
                        metric_value = calculate_angle_3d(p1, p2, p3)
                    else:  # HEIGHT
                        metric_value = visible_landmarks[idxs[0]]['y']
            except Exception as e:
                logger.error(f"Error calculando métrica '{metric_name}' en frame {frame_idx}: {e}")

            data[metric_name].append(metric_value)

    return pd.DataFrame.from_dict(data)


def count_repetitions(df_metrics: pd.DataFrame, params: ExerciseParams) -> int:
    """
    Wrapper unificado que cuenta repeticiones usando el robusto algoritmo de detección de valles.
    Recibe todos los parámetros a través del objeto de configuración.
    """
    angle_column = params.rep_counter_metric
    
    if df_metrics.empty or angle_column not in df_metrics.columns:
        logger.warning(f"No se puede contar repeticiones, falta la columna '{angle_column}'.")
        return 0

    angles = df_metrics[angle_column].ffill().bfill().to_numpy()
    if len(angles) == 0:
        return 0

    inverted_angles = -angles
    inverted_threshold = -params.low_thresh
    
    valleys, _ = find_peaks(
        inverted_angles, height=inverted_threshold, 
        prominence=params.peak_prominence, distance=params.peak_distance
    )
    
    logger.info(f"Detección de picos encontró {len(valleys)} repeticiones válidas.")
    return len(valleys)


def detect_faults(df_metrics: pd.DataFrame, rep_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Placeholder para la lógica de detección de fallos.
    """
    logger.info("La detección de fallos aún no está implementada.")
    return []
