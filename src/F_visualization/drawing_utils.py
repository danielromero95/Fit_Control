# src/F_visualization/drawing_utils.py
import cv2
import numpy as np
from typing import List, Dict
from mediapipe.python.solutions.pose import POSE_CONNECTIONS
from src.config import settings

def draw_landmarks_from_dicts(image: np.ndarray, landmarks: List[Dict]):
    if not landmarks: return

    h, w, _ = image.shape
    params = settings.drawing_params # Leemos los parámetros de estilo
    
    # Dibujar conexiones
    for connection in POSE_CONNECTIONS:
        start_idx, end_idx = connection
        if start_idx < len(landmarks) and end_idx < len(landmarks):
            start_point, end_point = landmarks[start_idx], landmarks[end_idx]
            if start_point.get('visibility', 0) > 0.5 and end_point.get('visibility', 0) > 0.5:
                cv2.line(image, (int(start_point['x']*w), int(start_point['y']*h)), (int(end_point['x']*w), int(end_point['y']*h)),
                         params.line_color_bgr, params.line_thickness)
    # Dibujar puntos
    for landmark in landmarks:
        if landmark.get('visibility', 0) > 0.5:
            cv2.circle(image, (int(landmark['x']*w), int(landmark['y']*h)),
                       params.point_radius, params.point_color_bgr, -1)