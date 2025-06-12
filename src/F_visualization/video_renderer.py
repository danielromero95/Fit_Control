# src/F_visualization/video_renderer.py (Versión Definitiva)

import cv2
import numpy as np
import logging
from src import config

logger = logging.getLogger(__name__)

def render_landmarks_on_video_hq(
    original_frames: list,
    landmarks_sequence: np.ndarray,
    crop_boxes: np.ndarray,
    output_path: str,
    fps: float
):
    """
    Dibuja landmarks (transformando coordenadas desde el crop) sobre los
    fotogramas originales de alta calidad y guarda el vídeo.
    """
    logger.info(f"Iniciando renderizado de vídeo HQ en: {output_path}")
    if not original_frames:
        logger.warning("No hay fotogramas para renderizar.")
        return

    orig_h, orig_w, _ = original_frames[0].shape
    proc_w, proc_h = config.DEFAULT_TARGET_WIDTH, config.DEFAULT_TARGET_HEIGHT
    
    # --- CAMBIO CLAVE: Calculamos los factores de escala ---
    scale_x = orig_w / proc_w
    scale_y = orig_h / proc_h

    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (orig_w, orig_h))
    if not writer.isOpened():
        logger.error(f"No se pudo abrir VideoWriter para la ruta: {output_path}")
        return

    for i, frame in enumerate(original_frames):
        annotated_frame = frame.copy()
        
        if i < len(landmarks_sequence) and landmarks_sequence[i] is not None:
            frame_landmarks = landmarks_sequence[i]
            if all(np.isnan(lm['x']) for lm in frame_landmarks):
                writer.write(annotated_frame)
                continue
            
            points_to_draw = {}
            crop_box = crop_boxes[i] if crop_boxes is not None and i < len(crop_boxes) else None

            if crop_box is not None and not np.isnan(crop_box).all():
                # Coordenadas del crop en el espacio de 256x256
                x1_p, y1_p, x2_p, y2_p = crop_box
                
                # --- CAMBIO CLAVE: Escalamos el crop box al tamaño original ---
                x1_o, y1_o = int(x1_p * scale_x), int(y1_p * scale_y)
                crop_w_o = int((x2_p - x1_p) * scale_x)
                crop_h_o = int((y2_p - y1_p) * scale_y)

                # Transformar coordenadas de landmark a píxeles absolutos en la imagen ORIGINAL
                for lm_idx, lm in enumerate(frame_landmarks):
                    if not np.isnan(lm['x']):
                        abs_x = x1_o + int(lm['x'] * crop_w_o)
                        abs_y = y1_o + int(lm['y'] * crop_h_o)
                        points_to_draw[lm_idx] = (abs_x, abs_y)
            
            # Dibujar esqueleto
            for p1_idx, p2_idx in config.POSE_CONNECTIONS:
                if p1_idx in points_to_draw and p2_idx in points_to_draw:
                    cv2.line(annotated_frame, points_to_draw[p1_idx], points_to_draw[p2_idx], config.CONNECTION_COLOR, 2)
            for point in points_to_draw.values():
                cv2.circle(annotated_frame, point, 4, config.LANDMARK_COLOR, -1)
        
        writer.write(annotated_frame)

    writer.release()
    logger.info("Vídeo de depuración HQ renderizado con éxito.")