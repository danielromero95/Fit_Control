# src/D_modeling/math_utils.py

import numpy as np

def calculate_angle_3d(p1, p2, p3):
    """Calcula el ángulo entre 3 puntos en el espacio 3D."""
    v1 = np.array([p1.x - p2.x, p1.y - p2.y, p1.z - p2.z])
    v2 = np.array([p3.x - p2.x, p3.y - p2.y, p3.z - p2.z])
    
    dot_product = np.dot(v1, v2)
    magnitude_v1 = np.linalg.norm(v1)
    magnitude_v2 = np.linalg.norm(v2)
    
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        return 180.0

    angle_rad = np.arccos(dot_product / (magnitude_v1 * magnitude_v2))
    return np.degrees(angle_rad)