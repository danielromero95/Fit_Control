# src/F_visualization/video_renderer.py

import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Definimos los puntos para dibujar las conexiones del esqueleto
POSE_CONNECTIONS = [(0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8), (9, 10), (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21), (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (11, 23), (12, 24), (23, 24), (23, 25), (25, 27), (27, 29), (27, 31), (24, 26), (26, 28), (28, 30), (28, 32), (29, 31), (30, 32)]

# --- CAMBIO CLAVE: Renombramos la función para que coincida con la importación ---
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
    
    # Intentamos importar las utilidades de MediaPipe de forma segura
    try:
        from mediapipe.python.solutions import drawing_utils as mp_drawing
        from mediapipe.python.solutions import pose as mp_pose
        from mediapipe.framework.formats import landmark_pb2
    except ImportError:
        logger.error("MediaPipe no está instalado. No se puede renderizar el vídeo de depuración.")
        return
        
    if not original_frames:
        logger.warning("No hay fotogramas para renderizar.")
        return

    height, width, _ = original_frames[0].shape
    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    if not writer.isOpened():
        logger.error(f"No se pudo abrir VideoWriter para la ruta: {output_path}")
        return

    for i, frame in enumerate(original_frames):
        annotated_frame = frame.copy()
        frame_landmarks = landmarks_sequence[i]
        
        if frame_landmarks is None or all(np.isnan(lm['x']) for lm in frame_landmarks):
            writer.write(annotated_frame)
            continue
            
        points_to_draw = {}
        
        # Obtenemos el bounding box del crop (si existe)
        crop_box = crop_boxes[i] if crop_boxes is not None and i < len(crop_boxes) else None
        
        # Si no hay crop_box, las coordenadas son relativas al frame completo
        x1, y1 = (crop_box[0], crop_box[1]) if crop_box is not None else (0, 0)
        crop_w = (crop_box[2] - crop_box[0]) if crop_box is not None else width
        crop_h = (crop_box[3] - crop_box[1]) if crop_box is not None else height
        
        # 1. Transformar coordenadas normalizadas a píxeles absolutos
        for lm_idx, lm in enumerate(frame_landmarks):
            if not np.isnan(lm['x']):
                abs_x = int(x1 + lm['x'] * crop_w)
                abs_y = int(y1 + lm['y'] * crop_h)
                points_to_draw[lm_idx] = (abs_x, abs_y)
        
        # 2. Dibujar conexiones (líneas) en rojo
        for p1_idx, p2_idx in POSE_CONNECTIONS:
            if p1_idx in points_to_draw and p2_idx in points_to_draw:
                cv2.line(annotated_frame, points_to_draw[p1_idx], points_to_draw[p2_idx], (0, 0, 255), 2)

        # 3. Dibujar landmarks (círculos) en verde
        for point in points_to_draw.values():
            cv2.circle(annotated_frame, point, 4, (0, 255, 0), -1)
            
        writer.write(annotated_frame)

    writer.release()
    logger.info("Vídeo de depuración HQ renderizado con éxito.")