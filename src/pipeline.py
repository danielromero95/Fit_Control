# src/pipeline.py (Actualizado)

import logging
import pandas as pd
import os
import cv2
from .A_preprocessing.frame_extraction import extract_and_preprocess_frames
# --- CAMBIO: Importamos desde los nuevos módulos ---
from .B_pose_estimation.processing import (
    extract_landmarks_from_frames,
    filter_and_interpolate_landmarks,
    calculate_metrics_from_sequence
)
from .D_modeling.count_reps import count_repetitions_from_df
from .F_visualization.video_renderer import render_landmarks_on_video_hq

logger = logging.getLogger(__name__)

def run_full_pipeline_in_memory(video_path: str, settings: dict, progress_callback=None):
    # ... (El contenido de esta función no necesita cambiar, ya que llamaba
    # a las funciones de alto nivel que ahora están en 'processing.py') ...
    def notify_progress(value):
        if progress_callback: progress_callback(value)

    notify_progress(5); logger.info("--- FASE 1: Extracción de Frames ---")
    original_frames, fps = extract_and_preprocess_frames(video_path, rotate=settings.get('rotate', 0), sample_rate=settings.get('sample_rate', 1))
    if not original_frames: raise ValueError("No se pudieron extraer fotogramas del vídeo.")

    target_size = (settings.get('target_width', 256), settings.get('target_height', 256))
    processed_frames = [cv2.resize(f, target_size) for f in original_frames]
    
    notify_progress(25); logger.info("--- FASE 2: Estimación de Pose ---")
    df_raw_landmarks = extract_landmarks_from_frames(frames=processed_frames, use_crop=settings.get('use_crop', True))

    notify_progress(50); logger.info("--- FASE 3: Filtrado e Interpolación ---")
    filtered_sequence, crop_boxes = filter_and_interpolate_landmarks(df_raw_landmarks)
    
    if settings.get('generate_debug_video', False):
        notify_progress(65); logger.info("--- FASE EXTRA: Renderizado de vídeo HQ ---")
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_dir = settings.get('output_dir', '.')
        os.makedirs(output_dir, exist_ok=True)
        output_video_path = os.path.join(output_dir, f"{base_name}_debug_HQ.mp4")
        render_landmarks_on_video_hq(original_frames, filtered_sequence, crop_boxes, output_video_path, fps)

    notify_progress(75); logger.info("--- FASE 4: Cálculo de Métricas ---")
    df_metrics = calculate_metrics_from_sequence(filtered_sequence, fps)
    
    notify_progress(90); logger.info("--- FASE 5: Conteo de Repeticiones ---")
    n_reps = count_repetitions_from_df(df_metrics)
    
    notify_progress(100); logger.info("--- PIPELINE COMPLETADO ---")
    
    return {"repeticiones_contadas": n_reps, "dataframe_metricas": df_metrics}