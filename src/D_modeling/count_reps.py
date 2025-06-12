# src/D_modeling/count_reps.py

import pandas as pd

def count_reps_from_angles(angle_sequence, low_thresh=90.0, high_thresh=160.0):
    """
    Cuenta repeticiones completas en una secuencia de ángulos.
    """
    reps = 0
    state = "idle"
    # Estados posibles:
    #   - "idle": aún no hemos encontrado un ángulo >= high_thresh para "iniciar" un rep
    #   - "up"  : estamos en zona alta (ángulo ≥ high_thresh), listos para bajar
    #   - "down": hemos bajado por debajo de low_thresh, esperamos subir para contar 1 rep

    for angle in angle_sequence:
        if state == "idle" and angle >= high_thresh:
            state = "up"
        elif state == "up" and angle < low_thresh:
            state = "down"
        elif state == "down" and angle >= high_thresh:
            reps += 1
            state = "up"
    return reps

def count_repetitions_from_df(
        df_metrics: pd.DataFrame,
        knee_column="rodilla_izq",
        low_thresh=90.0,
        high_thresh=160.0
    ):
    """
    Toma un DataFrame de métricas, extrae la columna de ángulo de rodilla
    y devuelve el número de repeticiones contadas.
    """
    if knee_column not in df_metrics.columns:
        raise ValueError(f"La columna '{knee_column}' no se encontró en el DataFrame de métricas.")

    # Rellenar NaN con un valor alto para no interferir en el conteo.
    angles = df_metrics[knee_column].fillna(high_thresh + 1.0).tolist()
    
    n_reps = count_reps_from_angles(angles, low_thresh=low_thresh, high_thresh=high_thresh)
    
    return n_reps