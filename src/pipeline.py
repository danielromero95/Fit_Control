# src/pipeline.py

import logging
import os
import pandas as pd
import cv2
from time import perf_counter
import math
from itertools import chain
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from typing import List, Dict, Any, Optional, Callable

# Importación de la configuración global desde nuestro sistema Pydantic/YAML
from src.config import settings as global_settings 
# Importación del resto de módulos de nuestra aplicación
from src.A_preprocessing.frame_extraction import extract_and_preprocess_frames
from src.B_pose_estimation.estimators import EstimationResult
from src.D_modeling.exercise_analyzer import calculate_metrics, count_repetitions, detect_faults
from src.F_visualization.drawing_utils import draw_landmarks_from_dicts

logger = logging.getLogger(__name__)


def _process_frame_chunk(frames_chunk: List[np.ndarray]) -> List[EstimationResult]:
    """
    Función worker que se ejecuta en un proceso separado.
    Procesa un "trozo" (chunk) de fotogramas. Es auto-contenida para ser segura
    en el multiprocesamiento.
    """
    # Importamos y creamos el estimador DENTRO del proceso hijo
    from src.B_pose_estimation.estimators import BaseEstimator, BlazePose3DEstimator, CroppedPoseEstimator
    from src.config import settings
    
    estimator: BaseEstimator = BlazePose3DEstimator() if settings.analysis_params.use_3d_analysis else CroppedPoseEstimator()
    
    results = []
    for frame in frames_chunk:
        try:
            result = estimator.estimate(frame)
            results.append(result)
        except Exception as e:
            logger.error(f"Error procesando un frame en un worker: {e}")
            results.append(EstimationResult(annotated_image=frame))
            
    estimator.close()
    return results


def run_full_pipeline_in_memory(
    video_path: str, 
    settings: Dict[str, Any], 
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> Dict[str, Any]:
    """
    Ejecuta el pipeline completo de análisis en memoria, desde la extracción
    de fotogramas hasta el análisis final, con procesamiento en paralelo.

    Args:
        video_path: Ruta al fichero de vídeo a analizar.
        settings: Diccionario con los ajustes de la sesión actual de la GUI (output_dir, rotate, etc.).
        progress_callback: Función opcional para reportar el progreso a la GUI.

    Returns:
        Un diccionario con los resultados del análisis, conteniendo:
        - "repeticiones_contadas": int
        - "dataframe_metricas": pd.DataFrame
        - "debug_video_path": str | None
        - "fallos_detectados": list[dict]
    """
    def notify(progress: int, message: str):
        logger.info(message)
        if progress_callback:
            progress_callback(progress)

    timings = {}; start_total = perf_counter()
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    output_dir = settings.get('output_dir', '.')
    session_dir = os.path.join(output_dir, base_name)
    os.makedirs(session_dir, exist_ok=True)

    try:
        mode = '3D' if global_settings.analysis_params.use_3d_analysis else '2D'
        notify(0, f"Inicializando pipeline en modo {mode}...")

        # --- FASE 1: Extracción ---
        t0 = perf_counter()
        notify(5, "FASE 1: Extrayendo fotogramas...")
        original_frames, fps = extract_and_preprocess_frames(video_path, settings.get('rotate'), settings.get('sample_rate', 1))
        timings['fase_1_extraction'] = perf_counter() - t0
        if not original_frames: raise ValueError("No se pudieron extraer fotogramas.")
        
        # --- PASO DE OPTIMIZACIÓN: Pre-redimensionado ---
        frames_to_process = original_frames
        if global_settings.performance_params.preprocess_size:
            t0_resize = perf_counter()
            w, h = global_settings.performance_params.preprocess_size
            logger.info(f"Redimensionando {len(original_frames)} frames a ({w}x{h}) para optimizar rendimiento...")
            frames_to_process = [cv2.resize(f, (w, h), interpolation=cv2.INTER_LINEAR) for f in original_frames]
            timings['fase_1a_resizing'] = perf_counter() - t0_resize
            
        # --- FASE 2: Estimación de Pose en Paralelo ---
        t0 = perf_counter()
        notify(15, "FASE 2: Estimando pose en paralelo...")
        
        workers = global_settings.performance_params.max_workers
        if workers <= 0: workers = max(1, os.cpu_count() - 1)
        
        chunk_size = math.ceil(len(frames_to_process) / workers)
        frame_chunks = [frames_to_process[i:i + chunk_size] for i in range(0, len(frames_to_process), chunk_size)]
        
        logger.info(f"Distribuyendo {len(frames_to_process)} fotogramas en {len(frame_chunks)} trozos para {workers} procesos.")
        
        with ProcessPoolExecutor(max_workers=workers) as executor:
            results_in_chunks = list(executor.map(_process_frame_chunk, frame_chunks))
        
        estimation_results = list(chain.from_iterable(results_in_chunks))
        
        notify(75, "FASE 2: Estimación de pose completada.")
        timings['fase_2_pose_estimation'] = perf_counter() - t0
        
        # --- FASE 3: Análisis Unificado y Data-Driven ---
        t0 = perf_counter()
        notify(80, "FASE 3: Analizando métricas y repeticiones...")

        # --- Pasamos la definición de métricas explícitamente ---
        df_metrics = calculate_metrics(
            estimation_results, 
            fps,
            metric_definitions=global_settings.squat_params.metric_definitions
        )
        
        n_reps = count_repetitions(df_metrics)
        faults_detected = detect_faults(df_metrics, {"reps": n_reps})
        timings['fase_3_analysis'] = perf_counter() - t0
        
        # --- FASE EXTRA: Renderizado de Vídeo de Alta Calidad ---
        debug_video_path = None
        if settings.get('generate_debug_video', global_settings.analysis_params.generate_debug_video):
            t0 = perf_counter()
            notify(98, "FASE EXTRA: Renderizando vídeo de depuración HQ...")
            annotated_frames_hq = []
            for original_frame, result in zip(original_frames, estimation_results):
                frame_to_draw = original_frame.copy()
                if result.landmarks:
                    draw_landmarks_from_dicts(frame_to_draw, result.landmarks)
                annotated_frames_hq.append(frame_to_draw)
            
            if annotated_frames_hq:
                height, width, _ = annotated_frames_hq[0].shape
                output_path = os.path.join(session_dir, f"{base_name}_debug.mp4")
                writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
                for fr in annotated_frames_hq: writer.write(fr)
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

    except Exception as e:
        logger.error(f"Error fatal en el pipeline: {e}", exc_info=True)
        raise