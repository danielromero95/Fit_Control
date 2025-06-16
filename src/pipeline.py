import logging
import os
import pandas as pd
import cv2
from time import perf_counter

from src.config import settings as global_settings # Renombramos para evitar colisión
from src.A_preprocessing.frame_extraction import extract_and_preprocess_frames
from src.B_pose_estimation.estimators import (
    BaseEstimator,
    CroppedPoseEstimator,
    BlazePose3DEstimator,
    EstimationResult
)
from src.D_modeling.exercise_analyzer import calculate_metrics, count_repetitions, detect_faults

logger = logging.getLogger(__name__)


def build_estimator() -> BaseEstimator:
    if global_settings.analysis_params.use_3d_analysis:
        return BlazePose3DEstimator()
    else:
        return CroppedPoseEstimator()


def run_full_pipeline_in_memory(video_path: str, settings: dict, progress_callback=None):
    def notify(progress: int, message: str):
        logger.info(message)
        if progress_callback:
            progress_callback(progress)

    timings = {}
    start_total = perf_counter()

    base_name = os.path.splitext(os.path.basename(video_path))[0]
    output_dir = settings.get('output_dir', '.')
    session_dir = os.path.join(output_dir, base_name)
    os.makedirs(session_dir, exist_ok=True)

    estimator = build_estimator()
    try:
        mode = '3D' if global_settings.analysis_params.use_3d_analysis else '2D'
        notify(0, f"Inicializando pipeline en modo {mode}...")

        t0 = perf_counter()
        notify(5, "FASE 1: Extrayendo fotogramas...")
        original_frames, fps = extract_and_preprocess_frames(video_path, settings.get('rotate'), settings.get('sample_rate', 1))
        timings['fase_1_extraction'] = perf_counter() - t0
        if not original_frames: raise ValueError("No se pudieron extraer fotogramas.")

        t0 = perf_counter()
        notify(15, "FASE 2: Estimando pose...")
        estimation_results = [estimator.estimate(frame) for frame in original_frames]
        timings['fase_2_pose_estimation'] = perf_counter() - t0
        
        t0 = perf_counter()
        notify(75, "FASE 3: Analizando métricas y repeticiones...")
        
        df_metrics = calculate_metrics(estimation_results, fps)
        n_reps = count_repetitions(df_metrics)
        faults_detected = detect_faults(df_metrics, {"reps": n_reps}) 

        timings['fase_3_analysis'] = perf_counter() - t0
        
        debug_video_path = None
        if settings.get('generate_debug_video', global_settings.analysis_params.generate_debug_video):
            t0 = perf_counter()
            notify(98, "FASE EXTRA: Renderizando vídeo de depuración...")
            annotated_frames = [res.annotated_image for res in estimation_results if res.annotated_image is not None]
            if annotated_frames:
                height, width, _ = annotated_frames[0].shape
                output_path = os.path.join(session_dir, f"{base_name}_debug.mp4")
                writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
                for fr in annotated_frames: writer.write(fr)
                writer.release()
                debug_video_path = output_path
            timings['fase_extra_video_render'] = perf_counter() - t0

        if settings.get('debug_mode', global_settings.analysis_params.debug_mode) and not df_metrics.empty:
            metric_file = os.path.join(session_dir, f"{base_name}_metrics.csv")
            df_metrics.to_csv(metric_file, index=False)
            logger.info(f"Métricas guardadas en: {metric_file}")
            
        timings['total_time'] = perf_counter() - start_total
        notify(100, "PIPELINE COMPLETADO")
        logger.info("--- RESUMEN DE RENDIMIENTO ---")
        for fase, t in timings.items(): logger.info(f"[TIMER] {fase:<25}: {t:>6.2f}s")
        
        return {"repeticiones_contadas": n_reps, "dataframe_metricas": df_metrics, "debug_video_path": debug_video_path, "fallos_detectados": faults_detected}
    finally:
        estimator.close()
        logger.info("Estimator cerrado correctamente.")