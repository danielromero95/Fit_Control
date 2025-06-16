# src/A_preprocessing/frame_extraction.py

import cv2
import os
import logging
from typing import List, Tuple, Optional

# --- CAMBIO CLAVE: Importamos la constante desde el fichero correcto ---
from src.constants import VIDEO_EXTENSIONS

logger = logging.getLogger(__name__)

def extract_and_preprocess_frames(
    video_path: str, 
    rotate: Optional[int] = None, 
    sample_rate: int = 1
) -> Tuple[List, float]:
    """
    Extrae fotogramas de un vídeo, los rota si es necesario y aplica un sample rate.
    """
    ext = os.path.splitext(video_path)[1].lower()
    
    # La comprobación ahora usa la constante importada directamente
    if ext not in VIDEO_EXTENSIONS:
        raise ValueError(f"Formato de vídeo no soportado: {ext}. Soportados: {VIDEO_EXTENSIONS}")

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"El fichero de vídeo no se encuentra en la ruta: {video_path}")

    logger.info(f"Iniciando extracción para: {video_path}")
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise IOError(f"No se pudo abrir el fichero de vídeo: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    logger.info(f"Propiedades del vídeo: {total_frames} frames, {fps:.2f} FPS")

    frames = []
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % sample_rate == 0:
            if rotate and rotate != 0:
                # Mapeamos los grados a las constantes de rotación de OpenCV
                if rotate == 90:
                    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                elif rotate == 180:
                    frame = cv2.rotate(frame, cv2.ROTATE_180)
                elif rotate == 270:
                    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            
            frames.append(frame)
        
        frame_count += 1

    cap.release()
    logger.info(f"Proceso completado. Se han extraído {len(frames)} fotogramas en memoria.")
    return frames, fps