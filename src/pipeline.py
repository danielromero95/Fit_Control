# src/pipeline.py

import logging
from .A_preprocessing.frame_extraction import extract_and_preprocess_frames
from .B_pose_estimation.pose_utils import (
    extract_landmarks_from_frames,
    filter_and_interpolate_landmarks,
    calculate_metrics_from_sequence
)
from .D_modeling.count_reps import count_repetitions_from_df

logger = logging.getLogger(__name__)

def run_full_pipeline_in_memory(video_path: str, settings: dict, progress_callback=None):
    """
    Ejecuta el pipeline completo de análisis en memoria.

    Args:
        video_path (str): Ruta al vídeo de entrada.
        settings (dict): Diccionario con parámetros como 'sample_rate', 'rotate', etc.
        progress_callback (callable, optional): Función para notificar el progreso.

    Returns:
        dict: Un diccionario con los resultados finales, como el conteo de repeticiones.
    """
    def notify_progress(value):
        if progress_callback:
            progress_callback(value)

    logger.info("--- INICIANDO FASE 1: Extracción de Frames ---")
    notify_progress(5)
    frames, fps = extract_and_preprocess_frames(
        video_path=video_path,
        sample_rate=settings.get('sample_rate', 1),
        rotate=settings.get('rotate', 0),
        target_width=settings.get('target_width', 256),
        target_height=settings.get('target_height', 256),
    )
    if not frames:
        raise ValueError("No se pudieron extraer fotogramas del vídeo.")

    logger.info("--- INICIANDO FASE 2: Estimación de Pose ---")
    notify_progress(25)
    df_raw_landmarks = extract_landmarks_from_frames(
        frames=frames,
        use_crop=settings.get('use_crop', False)
    )

    logger.info("--- INICIANDO FASE 3: Filtrado e Interpolación ---")
    notify_progress(50)
    # Nota: la función de filtrado en pose_utils debe ser completada
    # filtered_sequence = filter_and_interpolate_landmarks(df_raw_landmarks)
    
    logger.info("--- INICIANDO FASE 4: Cálculo de Métricas ---")
    notify_progress(75)
    # df_metrics = calculate_metrics_from_sequence(filtered_sequence, fps)
    
    logger.info("--- INICIANDO FASE 5: Conteo de Repeticiones ---")
    notify_progress(90)
    # n_reps = count_repetitions_from_df(df_metrics)
    
    # Mockup de resultados mientras se completan las funciones
    n_reps = 5 # Valor de ejemplo
    df_metrics = pd.DataFrame() # DataFrame vacío de ejemplo

    logger.info("--- PIPELINE COMPLETADO ---")
    notify_progress(100)
    
    return {
        "repeticiones_contadas": n_reps,
        "dataframe_metricas": df_metrics
    }