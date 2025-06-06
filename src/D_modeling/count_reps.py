# src/D_modeling/count_reps.py

import os
import pandas as pd
import argparse


def count_reps_from_angles(angle_sequence, low_thresh=90.0, high_thresh=160.0):
    """
    Cuenta cuántas repeticiones completas hay en una secuencia de ángulos de rodilla.
    Un ciclo completo se define como:
      1) EMPEZAR en 'parte alta' (ángulo >= high_thresh)
      2) BAJAR por debajo de low_thresh → 'down'
      3) SUBIR nuevamente hasta >= high_thresh → cuenta 1 rep

    Parámetros:
    -----------
    angle_sequence : lista o array de floats
        Serie temporal de ángulos (en grados) de la rodilla.
    low_thresh : float
        Umbral que indica 'fondo de la sentadilla' (< low_thresh).
    high_thresh : float
        Umbral que indica 'parte alta de la sentadilla' (>= high_thresh).

    Retorna:
    --------
    int
        Número de repeticiones detectadas.
    """
    reps = 0
    state = "idle"
    # Estados posibles:
    #   - "idle": aún no hemos encontrado un ángulo >= high_thresh para "iniciar" un rep
    #   - "up"  : estamos en zona alta (ángulo ≥ high_thresh), listos para bajar
    #   - "down": hemos bajado por debajo de low_thresh, esperamos subir para contar 1 rep

    for angle in angle_sequence:
        if state == "idle":
            # No contamos nada hasta que primero veamos un ángulo en la parte alta
            if angle >= high_thresh:
                state = "up"
        elif state == "up":
            # Si en 'up' vemos un ángulo < low_thresh, pasamos a 'down'
            if angle < low_thresh:
                state = "down"
        elif state == "down":
            # Si en 'down' subimos a ≥ high_thresh, contamos 1 rep y volvemos a 'up'
            if angle >= high_thresh:
                reps += 1
                state = "up"
        # demás casos (e.g. en 'up' con ángulos intermedios, en 'down' con ángulos intermedios, etc.)
        # simplemente no cambian el estado.
    return reps


def count_reps_main(input_metrics, output_count=None, knee_column="rodilla_izq",
                    low_thresh=90.0, high_thresh=160.0):
    """
    Lectura del CSV de métricas, extrae la columna de ángulo de rodilla indicada,
    aplica el conteo de repeticiones y guarda/retorna el resultado.

    Parámetros:
    -----------
    input_metrics : str
        Ruta al CSV que contiene las métricas generadas (incluyendo la columna de ángulo de rodilla).
    output_count : str o None
        Si se provee, ruta donde se guardará el número de repeticiones (como texto).
        Si es None, simplemente imprime el resultado en consola.
    knee_column : str
        Nombre de la columna que contiene el ángulo de rodilla a usar para el conteo.
    low_thresh : float
        Umbral para “fondo” de sentadilla.
    high_thresh : float
        Umbral para “parte alta” de sentadilla.
    """
    if not os.path.isfile(input_metrics):
        raise FileNotFoundError(f"El CSV de métricas no existe: {input_metrics}")

    df = pd.read_csv(input_metrics)

    if knee_column not in df.columns:
        raise ValueError(f"La columna '{knee_column}' no se encontró en el CSV de métricas.")

    # Extraer secuencia de ángulos, rellenar NaN con un valor muy alto (> high_thresh)
    # para que no interfiera en el conteo durante frames no detectados.
    angles = df[knee_column].fillna(high_thresh + 1.0).tolist()

    n_reps = count_reps_from_angles(angles, low_thresh=low_thresh, high_thresh=high_thresh)

    if output_count:
        os.makedirs(os.path.dirname(output_count), exist_ok=True)
        with open(output_count, "w", encoding="utf-8") as f:
            f.write(str(n_reps))
        print(f"Reps contadas = {n_reps}. Resultado guardado en: {output_count}")
    else:
        print(f"Reps contadas = {n_reps}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cuenta repeticiones (ciclos) en base a ángulos de rodilla del CSV de métricas."
    )
    parser.add_argument("--input_metrics", required=True,
                        help="Ruta al CSV que contiene las métricas por frame (ángulo de rodilla).")
    parser.add_argument("--output_count", default=None,
                        help="Archivo donde guardar el número de repeticiones (opcional).")
    parser.add_argument("--knee_column", default="rodilla_izq",
                        help="Nombre de la columna del ángulo de rodilla en el CSV (por defecto: 'rodilla_izq').")
    parser.add_argument("--low_thresh", type=float, default=90.0,
                        help="Umbral para considerar 'fondo' de sentadilla (< low_thresh).")
    parser.add_argument("--high_thresh", type=float, default=160.0,
                        help="Umbral para considerar 'parte alta' de sentadilla (>= high_thresh).")

    args = parser.parse_args()

    count_reps_main(
        input_metrics=args.input_metrics,
        output_count=args.output_count,
        knee_column=args.knee_column,
        low_thresh=args.low_thresh,
        high_thresh=args.high_thresh
    )
