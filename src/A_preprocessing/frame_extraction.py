# src/A_preprocessing/frame_extraction.py

import cv2
import os
import logging
import numpy as np

logger = logging.getLogger(__name__)

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".mpg", ".mpeg", ".wmv"}

def extract_and_preprocess_frames(
        video_path,
        sample_rate=1,
        rotate=0,
        target_width=256,
        target_height=256,
        progress_callback=None
    ):
    """
    Extrae fotogramas de un vídeo, los preprocesa (rota, redimensiona)
    y los devuelve como una lista de imágenes en memoria.

    Devuelve:
    ----------
    (list[np.ndarray], float)
        Una tupla conteniendo:
        - Una lista de fotogramas (imágenes como arrays de NumPy en formato BGR).
        - Los FPS (fotogramas por segundo) del vídeo original.
    """
    logger.info(f"Iniciando extracción y preprocesamiento para: {video_path}")

    ext = os.path.splitext(video_path)[1].lower()
    if ext not in VIDEO_EXTENSIONS:
        raise ValueError(f"Extensión de vídeo no soportada: '{ext}'.")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"No se pudo abrir el vídeo: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    logger.info(f"Propiedades del vídeo: {frame_count} frames, {fps:.2f} FPS")

    processed_frames = []
    idx = 0
    last_percent_done = -1

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if progress_callback and frame_count > 0:
            percent_done = int((idx / frame_count) * 100)
            if percent_done > last_percent_done:
                progress_callback(percent_done)
                last_percent_done = percent_done

        if idx % sample_rate == 0:
            if rotate == 90:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            elif rotate == 180:
                frame = cv2.rotate(frame, cv2.ROTATE_180)
            elif rotate == 270:
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

            frame = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_AREA)
            
            processed_frames.append(frame)
        
        idx += 1

    cap.release()
    logger.info(f"Proceso completado. Se han extraído y preprocesado {len(processed_frames)} fotogramas en memoria.")

    return processed_frames, fps