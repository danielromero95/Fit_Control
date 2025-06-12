# src/pipeline.py
import logging
import pandas as pd
import os
import cv2
from src import config
from src.A_preprocessing.frame_extraction import extract_and_preprocess_frames
from src.B_pose_estimation.processing import extract_landmarks_from_frames, filter_and_interpolate_landmarks, calculate_metrics_from_sequence
from src.D_modeling.count_reps import count_repetitions_from_df
from src.F_visualization.video_renderer import render_landmarks_on_video_hq

logger = logging.getLogger(__name__)

def run_full_pipeline_in_memory(video_path: str, settings: dict, progress_callback=None):
    def notify(value):
        if progress_callback: progress_callback(value)

    base_name = os.path.splitext(os.path.basename(video_path))[0]
    output_dir = settings.get('output_dir', '.')
    session_dir = os.path.join(output_dir, base_name)
    os.makedirs(session_dir, exist_ok=True)
        
    notify(5); logger.info("FASE 1: Extracción")
    original_frames, fps = extract_and_preprocess_frames(video_path, rotate=settings.get('rotate', 0), sample_rate=settings.get('sample_rate', 1))
    target_size = (settings.get('target_width'), settings.get('target_height'))
    processed_frames = [cv2.resize(f, target_size) for f in original_frames]
    
    notify(25); logger.info("FASE 2: Estimación de Pose")
    df_raw_landmarks = extract_landmarks_from_frames(frames=processed_frames, use_crop=settings.get('use_crop', True))

    notify(50); logger.info("FASE 3: Filtrado")
    filtered_sequence, crop_boxes = filter_and_interpolate_landmarks(df_raw_landmarks)
    
    if settings.get('generate_debug_video', False):
        notify(65); logger.info("FASE EXTRA: Renderizado de vídeo HQ")
        output_video_path = os.path.join(session_dir, f"{base_name}_3_debug_HQ.mp4")
        render_landmarks_on_video_hq(original_frames, filtered_sequence, crop_boxes, output_video_path, fps)

    notify(75); logger.info("FASE 4: Métricas")
    df_metrics = calculate_metrics_from_sequence(filtered_sequence, fps)
    
    notify(90); logger.info("FASE 5: Conteo")
    n_reps = count_repetitions_from_df(df_metrics)
    
    if settings.get('debug_mode', False):
        logger.info("MODO DEPURACIÓN: Guardando datos intermedios")
        df_raw_landmarks.to_csv(os.path.join(session_dir, f"{base_name}_1_raw_landmarks.csv"), index=False)
        df_metrics.to_csv(os.path.join(session_dir, f"{base_name}_2_metrics.csv"), index=False)

    notify(100); logger.info("PIPELINE COMPLETADO")
    return {"repeticiones_contadas": n_reps, "dataframe_metricas": df_metrics}