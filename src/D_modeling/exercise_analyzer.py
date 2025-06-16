# src/D_modeling/exercise_analyzer.py
"""
Módulo central y unificado para todo el análisis de ejercicios.
Contiene la lógica para calcular métricas, contar repeticiones y detectar fallos.
"""
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import logging
from typing import List, Tuple

# Importaciones de nuestros propios módulos
from src.config import settings
from src.B_pose_estimation.estimators import EstimationResult
from src.D_modeling.math_utils import calculate_angle_3d

try:
    import mediapipe as mp
    PoseLandmark = mp.solutions.pose.PoseLandmark
except ImportError:
    PoseLandmark = None

logger = logging.getLogger(__name__)


def calculate_metrics(estimation_results: List[EstimationResult], fps: int) -> pd.DataFrame:
    """
    Función unificada para calcular métricas clave a partir de los resultados de estimación.
    """
    if not PoseLandmark:
        logger.error("MediaPipe no está disponible para calcular métricas.")
        return pd.DataFrame()

    metrics_list = []
    is_3d_mode = any(res.world_landmarks for res in estimation_results if res)

    for frame_idx, result in enumerate(estimation_results):
        landmarks_source = result.world_landmarks if is_3d_mode and result.world_landmarks else result.landmarks
        if not landmarks_source:
            continue
        
        # Esta construcción de diccionario ya es correcta
        landmarks = {lm_name.name: landmarks_source[lm_name.value] for lm_name in PoseLandmark}
        
        left_shoulder = landmarks.get('LEFT_SHOULDER')
        left_hip = landmarks.get('LEFT_HIP')
        left_knee = landmarks.get('LEFT_KNEE')
        left_ankle = landmarks.get('LEFT_ANKLE')

        if all([left_shoulder, left_hip, left_knee, left_ankle]):
            knee_angle = calculate_angle_3d(left_hip, left_knee, left_ankle)
            hip_angle = calculate_angle_3d(left_shoulder, left_hip, left_knee)
            
            # --- Usamos acceso por clave ['y'] en lugar de .y ---
            hip_height = left_hip['y']
        else:
            knee_angle, hip_angle, hip_height = None, None, None

        metrics_list.append({
            'frame_idx': frame_idx,
            'time_s': frame_idx / fps,
            'rodilla_izq': knee_angle,
            'cadera_izq': hip_angle,
            'altura_cadera': hip_height,
        })

    return pd.DataFrame(metrics_list)


def count_repetitions(df_metrics: pd.DataFrame) -> int:
    """
    Wrapper unificado que cuenta repeticiones usando el robusto algoritmo de detección de valles.
    """
    if df_metrics.empty or 'rodilla_izq' not in df_metrics.columns:
        logger.warning("No se puede contar repeticiones, faltan datos de ángulo de rodilla.")
        return 0

    angles = df_metrics['rodilla_izq'].ffill().bfill().tolist()
    if not angles:
        return 0

    # Invertimos la señal para que los valles se conviertan en picos
    inverted_angles = -np.array(angles)
    inverted_threshold = -settings.squat_params.low_thresh
    
    valleys, _ = find_peaks(
        inverted_angles, 
        height=inverted_threshold, 
        prominence=settings.squat_params.peak_prominence, 
        distance=settings.squat_params.peak_distance
    )
    
    logger.info(f"Detección de picos encontró {len(valleys)} repeticiones válidas.")
    return len(valleys)


def detect_faults(df_metrics: pd.DataFrame, rep_data: dict) -> List[dict]:
    """
    Placeholder para la lógica de detección de fallos.
    Aquí es donde se cargaría y usaría el modelo de Machine Learning.
    """
    # TODO: Implementar la carga del modelo .joblib y la predicción.
    # Por ahora, devolvemos una lista vacía.
    logger.info("La detección de fallos por IA aún no está implementada.")
    faults = []
    
    # Se podría añadir aquí la lógica de fallo de profundidad por reglas si se desea
    
    return faults