# src/F_visualization/video_renderer.py
import cv2
import numpy as np
import logging
from src import config

logger = logging.getLogger(__name__)

def render_landmarks_on_video_hq(original_frames: list, landmarks_sequence: np.ndarray, crop_boxes: np.ndarray, output_path: str, fps: float):
    logger.info(f"Iniciando renderizado de vídeo HQ en: {output_path}")
    if not original_frames: return
    height, width, _ = original_frames[0].shape
    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    if not writer.isOpened():
        logger.error(f"No se pudo abrir VideoWriter para la ruta: {output_path}")
        return

    for i, frame in enumerate(original_frames):
        annotated_frame = frame.copy()
        if i < len(landmarks_sequence) and landmarks_sequence[i] is not None:
            frame_landmarks = landmarks_sequence[i]
            if all(np.isnan(lm['x']) for lm in frame_landmarks):
                writer.write(annotated_frame); continue
            
            points_to_draw = {}
            crop_box = crop_boxes[i] if crop_boxes is not None and i < len(crop_boxes) else None
            x1, y1 = (crop_box[0], crop_box[1]) if crop_box is not None else (0, 0)
            crop_w = (crop_box[2] - crop_box[0]) if crop_box is not None else width
            crop_h = (crop_box[3] - crop_box[1]) if crop_box is not None else height
            
            for lm_idx, lm in enumerate(frame_landmarks):
                if not np.isnan(lm['x']):
                    abs_x = int(x1 + lm['x'] * crop_w)
                    abs_y = int(y1 + lm['y'] * crop_h)
                    points_to_draw[lm_idx] = (abs_x, abs_y)
            
            for p1_idx, p2_idx in config.POSE_CONNECTIONS:
                if p1_idx in points_to_draw and p2_idx in points_to_draw:
                    cv2.line(annotated_frame, points_to_draw[p1_idx], points_to_draw[p2_idx], config.CONNECTION_COLOR, 2)
            for point in points_to_draw.values():
                cv2.circle(annotated_frame, point, 4, config.LANDMARK_COLOR, -1)
        writer.write(annotated_frame)
    writer.release()
    logger.info("Vídeo de depuración HQ renderizado con éxito.")