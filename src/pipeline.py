# src/pipeline.py

import logging
import pandas as pd
import os
import cv2
from .A_preprocessing.frame_extraction import extract_and_preprocess_frames
from .B_pose_estimation.pose_utils import (
    extract_landmarks_from_frames,
    filter_and_interpolate_landmarks,
    calculate_metrics_from_sequence
)
from .D_modeling.count_reps import count_repetitions_from_df
from .F_visualization.video_renderer import render_landmarks_on_video

logger = logging.getLogger(__name__)

def run_full_pipeline_in_memory(video_path: str, settings: dict, progress_callback=None):
    def notify_progress(value):
        if progress_callback:
            progress_callback(value)

    # --- FASE 1: Extracción de Frames ---
    logger.info("--- INICIANDO FASE 1: Extracción de Frames ---")
    notify_progress(5)
    original_frames, fps = extract_and_preprocess_frames(
        video_path=video_path,
        rotate=settings.get('rotate', 0),
        sample_rate=settings.get('sample_rate', 1)
    )
    if not original_frames:
        raise ValueError("No se pudieron extraer fotogramas del vídeo.")

    # --- Preprocesamiento (Redimensionado) ---
    target_size = (settings.get('target_width', 256), settings.get('target_height', 256))
    processed_frames = [cv2.resize(f, target_size) for f in original_frames]
    
    # --- FASE 2: Estimación de Pose ---
    logger.info("--- INICIANDO FASE 2: Estimación de Pose ---")
    notify_progress(25)
    df_raw_landmarks = extract_landmarks_from_frames(
        frames=processed_frames,
        use_crop=settings.get('use_crop', False)
    )

    # --- FASE 3: Filtrado e Interpolación ---
    logger.info("--- INICIANDO FASE 3: Filtrado e Interpolación ---")
    notify_progress(50)
    filtered_sequence = filter_and_interpolate_landmarks(df_raw_landmarks)
    
    # --- FASE EXTRA: Visualización ---
    if settings.get('generate_debug_video', False):
        logger.info("--- INICIANDO FASE EXTRA: Renderizado de vídeo de depuración ---")
        notify_progress(65)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        # Asegurarse de que el directorio de salida existe
        output_dir = settings.get('output_dir', '.')
        os.makedirs(output_dir, exist_ok=True)
        output_video_path = os.path.join(output_dir, f"{base_name}_debug.mp4")
        
        # Le pasamos los frames ORIGINALES para un vídeo de buena calidad
        render_landmarks_on_video(original_frames, filtered_sequence, output_video_path, fps)

    # --- FASE 4: Cálculo de Métricas ---
    logger.info("--- INICIANDO FASE 4: Cálculo de Métricas ---")
    notify_progress(75)
    df_metrics = calculate_metrics_from_sequence(filtered_sequence, fps)
    
    # --- FASE 5: Conteo de Repeticiones ---
    logger.info("--- INICIANDO FASE 5: Conteo de Repeticiones ---")
    notify_progress(90)
    n_reps = count_repetitions_from_df(df_metrics)
    
    logger.info("--- PIPELINE COMPLETADO ---")
    notify_progress(100)
    
    return {"repeticiones_contadas": n_reps, "dataframe_metricas": df_metrics}