# src/D_modeling/math_utils.py

import numpy as np
from typing import Dict

def calculate_angle_3d(p1: Dict, p2: Dict, p3: Dict) -> float:
    """
    Calcula el ángulo ∡p1–p2–p3 en espacio 3D.
    Ahora asume que p1, p2, p3 son diccionarios con claves 'x', 'y', 'z'.
    """
    # --- Usamos acceso por clave ['x'] en lugar de por atributo .x ---
    v1 = np.array([p1['x'] - p2['x'], p1['y'] - p2['y'], p1['z'] - p2['z']])
    v2 = np.array([p3['x'] - p2['x'], p3['y'] - p2['y'], p3['z'] - p2['z']])

    dot_product = np.dot(v1, v2)
    norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)
    
    norm_product += 1e-8 

    cos_angle = np.clip(dot_product / norm_product, -1.0, 1.0)
    angle_rad = np.arccos(cos_angle)
    
    return np.degrees(angle_rad)