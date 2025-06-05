import numpy as np
from scipy.signal import find_peaks

def count_reps(angle_sequence, fps, prominence=10, distance=0.5):
    """
    Cuenta repeticiones a partir de secuencia de ángulo de cadera (por ejemplo).
    - prominence: altura mínima del pico (en grados).
    - distance: distancia mínima en segundos entre picos.
    Retorna número de repeticiones.
    """
    # Convertir distance en número de muestras
    min_distance_samples = int(distance * fps)
    peaks, _ = find_peaks(angle_sequence, prominence=prominence, distance=min_distance_samples)
    return len(peaks)
