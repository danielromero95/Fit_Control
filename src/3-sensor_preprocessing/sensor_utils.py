import pandas as pd
import numpy as np

# Funciones para cargar y procesar datos del sensor desde CSV
def load_sensor_data(csv_path):
    """
    Carga CSV y retorna DataFrame con índices de timestamp en ms como int.
    """
    df = pd.read_csv(csv_path)
    df['timestamp_ms'] = df['timestamp_ms'].astype(int)
    # Ordenar por timestamp
    df = df.sort_values('timestamp_ms').reset_index(drop=True)
    return df

# Alineación de timestamps del sensor con el vídeo
def align_timestamps(video_start_ts, sensor_df):
    """
    Recibe:
    - video_start_ts: timestamp en ms correspondiente a fotograma 0.
    - sensor_df: DataFrame con columna 'timestamp_ms'.
    Retorna DataFrame con nueva columna 'timestamp_corrected'.
    """
    offset = video_start_ts - sensor_df['timestamp_ms'].iloc[0]
    sensor_df['timestamp_corrected'] = sensor_df['timestamp_ms'] + offset
    return sensor_df

# Interpolación de datos del sensor a los fotogramas del vídeo
def interpolate_sensor_to_video(sensor_df, video_frame_ts):
    """
    sensor_df: DataFrame con 'timestamp_corrected' y columnas de valor (ax, ay, az, heart_rate).
    video_frame_ts: lista de timestamps (ms) de cada fotograma (por ejemplo, [t0, t1, ...]).
    Retorna DataFrame con índices frame y columnas interpoladas.
    """
    # Preparar arrays
    sensor_times = sensor_df['timestamp_corrected'].values
    ax = sensor_df['ax'].values
    ay = sensor_df['ay'].values
    az = sensor_df['az'].values
    hr = sensor_df['heart_rate'].values

    interp_ax = np.interp(video_frame_ts, sensor_times, ax)
    interp_ay = np.interp(video_frame_ts, sensor_times, ay)
    interp_az = np.interp(video_frame_ts, sensor_times, az)
    interp_hr = np.interp(video_frame_ts, sensor_times, hr)
    # Crear DataFrame de salida
    df_interp = pd.DataFrame({
        'timestamp_frame': video_frame_ts,
        'ax': interp_ax,
        'ay': interp_ay,
        'az': interp_az,
        'heart_rate': interp_hr
    })
    return df_interp

# Llenado de huecos cortos en datos del sensor
def fill_short_gaps(sensor_df, max_gap_ms=200, long_gap_ms=1000):
    """
    Llena huecos de hasta `max_gap_ms` con forward-fill.
    Si un segmento supera `long_gap_ms`, marca filas como faltantes.
    Asume que sensor_df está ordenado y con frecuencia variable.
    Retorna DataFrame con columnas originales + 'status' (OK, short_fill, missing).
    """
    df = sensor_df.copy()
    df['status'] = 'OK'
    times = df['timestamp_ms'].values
    for i in range(1, len(times)):
        gap = times[i] - times[i-1]
        if gap <= max_gap_ms:
            # No hacer nada (datos continuos)
            continue
        elif gap <= long_gap_ms:
            # Rellenar entre i-1 e i
            df.loc[i, ['ax','ay','az','heart_rate']] = df.loc[i-1, ['ax','ay','az','heart_rate']].values
            df.loc[i, 'status'] = 'short_fill'
        else:
            # Hueco largo: marcar como missing
            df.loc[i, 'status'] = 'missing'
    return df


# Preprocesamiento de datos del sensor: conversión de unidades
def convert_units(sensor_df):
    """
    Convierte ax, ay, az de g a m/s² asumiendo que vienen en g.
    Verifica que heart_rate esté en bpm (si hay un factor de escala, convertir).
    """
    df = sensor_df.copy()
    df['ax'] = df['ax'] * 9.81
    df['ay'] = df['ay'] * 9.81
    df['az'] = df['az'] * 9.81
    # Suponemos hr ya en bpm
    return df



