# src/F_visualization/drawing_utils.py

import cv2
import numpy as np
from typing import List, Dict, Tuple
from mediapipe.python.solutions.pose import POSE_CONNECTIONS

def draw_landmarks_from_dicts(
    image: np.ndarray, 
    landmarks: List[Dict], 
    line_color: Tuple[int, int, int],
    point_color: Tuple[int, int, int],
    line_thickness: int,
    point_radius: int
):
    """
    Dibuja landmarks y conexiones en una imagen a partir de una lista de diccionarios
    y parámetros de estilo explícitos.
    """
    if not landmarks:
        return

    h, w, _ = image.shape
    
    # Dibujar las conexiones
    for connection in POSE_CONNECTIONS:
        start_idx, end_idx = connection
        if start_idx < len(landmarks) and end_idx < len(landmarks):
            start_point, end_point = landmarks[start_idx], landmarks[end_idx]
            if start_point and end_point and start_point.get('visibility', 0) > 0.5 and end_point.get('visibility', 0) > 0.5:
                cv2.line(image, 
                         (int(start_point['x'] * w), int(start_point['y'] * h)), 
                         (int(end_point['x'] * w), int(end_point['y'] * h)),
                         line_color, line_thickness)

    # Dibujar los puntos (landmarks)
    for landmark in landmarks:
        if landmark and landmark.get('visibility', 0) > 0.5:
            cv2.circle(image, 
                       (int(landmark['x'] * w), int(landmark['y'] * h)), 
                       point_radius, point_color, -1)
