# src/B_pose_estimation/pose_utils.py
"""
Librería para la estimación de pose y el cálculo de métricas.

Este módulo contiene la lógica para:
1.  Detectar landmarks de pose usando MediaPipe, con y sin recorte centrado.
2.  Extraer landmarks de una secuencia de imágenes (en memoria) a un DataFrame.
3.  Filtrar e interpolar los datos de landmarks.
4.  Calcular métricas biomecánicas (ángulos, distancias, velocidades) a partir de los landmarks.

Las clases y funciones están diseñadas para operar con objetos de Python (NumPy, Pandas)
en lugar de leer/escribir archivos intermedios, permitiendo su uso en pipelines
de memoria como el de la GUI principal.
"""
import cv2
import numpy as np
import math
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# =================================================================================
# 1. CLASES ESTIMATOR (ENCAPSULAN MEDIAPIPE)
# =================================================================================

class PoseEstimator:
    """
    Encapsula MediaPipe Pose (sin cropping).
    La importación de MediaPipe se hace en el constructor para no bloquear
    la importación de este módulo en entornos sin mediapipe instalado.
    """
    def __init__(self, static_image_mode=True, model_complexity=1, min_detection_confidence=0.5):
        try:
            from mediapipe.python.solutions import pose as mp_pose_module
            from mediapipe.python.solutions import drawing_utils as mp_drawing_utils
        except ImportError:
            logger.error("MediaPipe no está instalado. Por favor, instálalo para usar PoseEstimator.")
            raise

        self.mp_pose_module = mp_pose_module
        self.mp_drawing_utils = mp_drawing_utils
        self.pose = self.mp_pose_module.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence
        )

    def estimate_pose(self, image):
        """
        Estima la pose en una imagen BGR.
        Retorna (landmarks, annotated_image).
        """
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(img_rgb)

        if not results.pose_landmarks:
            return None, image

        landmarks = [{'x': lm.x, 'y': lm.y, 'z': lm.z, 'visibility': lm.visibility} for lm in results.pose_landmarks.landmark]
        
        annotated_image = image.copy()
        self.mp_drawing_utils.draw_landmarks(
            annotated_image, results.pose_landmarks, self.mp_pose_module.POSE_CONNECTIONS
        )
        return landmarks, annotated_image

    def close(self):
        self.pose.close()

class CroppedPoseEstimator:
    """
    Wrapper de MediaPipe que realiza una detección en dos pasadas para
    enfocarse en la persona (cropping).
    """
    def __init__(self, static_image_mode=True, model_complexity=1, min_detection_confidence=0.5, crop_margin=0.15, target_size=(256, 256)):
        self.crop_margin = crop_margin
        self.target_size = target_size
        try:
            from mediapipe.python.solutions import pose as mp_pose_module
            from mediapipe.python.solutions import drawing_utils as mp_drawing_utils
        except ImportError:
            logger.error("MediaPipe no está instalado. Por favor, instálalo para usar CroppedPoseEstimator.")
            raise
        
        self.mp_pose_module = mp_pose_module
        self.mp_drawing_utils = mp_drawing_utils
        self.pose_full = self.mp_pose_module.Pose(static_image_mode=static_image_mode, model_complexity=model_complexity, min_detection_confidence=min_detection_confidence)
        self.pose_crop = self.mp_pose_module.Pose(static_image_mode=static_image_mode, model_complexity=model_complexity, min_detection_confidence=min_detection_confidence)

    def estimate_and_crop(self, image_bgr):
        """
        Detecta, recorta la persona y vuelve a detectar para mayor precisión.
        Retorna (landmarks_del_crop, imagen_del_crop_anotada).
        """
        h0, w0 = image_bgr.shape[:2]
        img_rgb_full = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        results_full = self.pose_full.process(img_rgb_full)

        if not results_full.pose_landmarks:
            return None, image_bgr

        lms_full = results_full.pose_landmarks.landmark
        xy_full = np.array([[lm.x * w0, lm.y * h0] for lm in lms_full])
        x_min, y_min = xy_full.min(axis=0)
        x_max, y_max = xy_full.max(axis=0)

        dx, dy = (x_max - x_min) * self.crop_margin, (y_max - y_min) * self.crop_margin
        x1, y1 = max(int(x_min - dx), 0), max(int(y_min - dy), 0)
        x2, y2 = min(int(x_max + dx), w0), min(int(y_max + dy), h0)

        crop = image_bgr[y1:y2, x1:x2]
        if crop.size == 0:
            return None, image_bgr

        crop_resized = cv2.resize(crop, self.target_size, interpolation=cv2.INTER_LINEAR)
        crop_rgb = cv2.cvtColor(crop_resized, cv2.COLOR_BGR2RGB)
        results_crop = self.pose_crop.process(crop_rgb)

        annotated_crop = crop_resized.copy()
        if results_crop.pose_landmarks:
            landmarks_crop = [{'x': lm.x, 'y': lm.y, 'z': lm.z, 'visibility': lm.visibility} for lm in results_crop.pose_landmarks.landmark]
            self.mp_drawing_utils.draw_landmarks(annotated_crop, results_crop.pose_landmarks, self.mp_pose_module.POSE_CONNECTIONS)
        else:
            landmarks_crop = None
        
        return landmarks_crop, annotated_crop

    def close(self):
        self.pose_full.close()
        self.pose_crop.close()

# =================================================================================
# 2. FUNCIONES DE LÓGICA DE PIPELINE (OPERAN EN MEMORIA)
# =================================================================================

def extract_landmarks_from_frames(frames: list, use_crop: bool = False, visibility_threshold: float = 0.5):
    """
    Toma una lista de imágenes (frames), extrae los landmarks de cada una
    y devuelve un DataFrame de pandas con los resultados.
    """
    logger.info(f"Extrayendo landmarks de {len(frames)} frames. Usando crop: {use_crop}")
    estimator = CroppedPoseEstimator(min_detection_confidence=visibility_threshold) if use_crop else PoseEstimator(min_detection_confidence=visibility_threshold)
    
    rows = []
    for i, img in enumerate(frames):
        landmarks, _ = estimator.estimate_and_crop(img) if use_crop else estimator.estimate_pose(img)
        
        row = {"frame_idx": i}
        if landmarks:
            for lm_idx, pt in enumerate(landmarks):
                row[f"x{lm_idx}"] = pt['x']
                row[f"y{lm_idx}"] = pt['y']
                row[f"z{lm_idx}"] = pt['z']
                row[f"v{lm_idx}"] = pt['visibility']
        else: # Si no se detectan landmarks, rellenar con NaN
            for lm_idx in range(33):
                row.update({f"x{lm_idx}": np.nan, f"y{lm_idx}": np.nan, f"z{lm_idx}": np.nan, f"v{lm_idx}": np.nan})
        rows.append(row)
        
    estimator.close()
    return pd.DataFrame(rows)

def filter_and_interpolate_landmarks(df_raw: pd.DataFrame, min_confidence: float = 0.5):
    """
    Toma un DataFrame de landmarks raw, filtra los puntos de baja confianza,
    interpola los huecos y devuelve un array NumPy de secuencias de landmarks.
    """
    logger.info(f"Filtrando e interpolando {len(df_raw)} frames de landmarks.")
    n_frames = len(df_raw)
    n_points = 33
    
    # El array tiene 4 columnas: x, y, z, visibility
    arr = np.full((n_frames, n_points, 4), np.nan, dtype=float)
    
    # Poblar el array con datos válidos del DataFrame
    for t, (_, row) in enumerate(df_raw.iterrows()):
        for i in range(n_points):
            visibility = row.get(f"v{i}", np.nan)
            if pd.notna(visibility) and visibility >= min_confidence:
                arr[t, i, 0] = row.get(f"x{i}")
                arr[t, i, 1] = row.get(f"y{i}")
                arr[t, i, 2] = row.get(f"z{i}")
                arr[t, i, 3] = visibility

    # Interpolar cada coordenada de landmark a lo largo del tiempo
    for i in range(n_points):
        valid_mask = ~np.isnan(arr[:, i, 0])
        valid_indices = np.where(valid_mask)[0]
        if len(valid_indices) > 1: # Se necesita más de un punto para interpolar
            interp_indices = np.arange(n_frames)
            for j in range(3): # Interpolar X, Y, y Z
                arr[:, i, j] = np.interp(interp_indices, valid_indices, arr[valid_indices, i, j])

    # Reconstruir la lista de diccionarios desde el array de NumPy
    filtered_sequence = []
    for t in range(n_frames):
        frame_landmarks = [{'x': arr[t, i, 0], 'y': arr[t, i, 1], 'z': arr[t, i, 2], 'visibility': arr[t, i, 3] if pd.notna(arr[t, i, 3]) else 0.0} for i in range(n_points)]
        filtered_sequence.append(frame_landmarks)
        
    return np.array(filtered_sequence, dtype=object)

def calculate_metrics_from_sequence(sequence: np.ndarray, fps: float):
    """
    Toma una secuencia de landmarks filtrada y los fps, y devuelve
    un DataFrame con todas las métricas biomecánicas calculadas.
    """
    logger.info(f"Calculando métricas para una secuencia de {len(sequence)} frames.")
    all_metrics = []
    for idx, frame_landmarks in enumerate(sequence):
        row = {"frame_idx": idx}
        # Comprobamos si el primer landmark es inválido como indicador de todo el frame
        if frame_landmarks is None or pd.isna(frame_landmarks[0]['x']):
            row.update({ 'rodilla_izq': np.nan, 'rodilla_der': np.nan, 'codo_izq': np.nan, 'codo_der': np.nan, 'anchura_hombros': np.nan, 'separacion_pies': np.nan })
        else:
            norm_lm = normalize_landmarks(frame_landmarks)
            angles = extract_joint_angles(norm_lm)
            dists = calculate_distances(norm_lm)
            row.update(angles)
            row.update(dists)
        all_metrics.append(row)
    
    dfm = pd.DataFrame(all_metrics)
    if dfm.empty: return dfm

    # Calcular velocidades y simetrías
    dfm_filled = dfm.ffill().bfill()
    for col in ['rodilla_izq', 'rodilla_der', 'codo_izq', 'codo_der']:
        dfm[f"vel_ang_{col}"] = calculate_angular_velocity(dfm_filled[col].tolist(), fps)
        
    dfm["sim_rodilla"] = dfm.apply(lambda r: calculate_symmetry(r['rodilla_izq'], r['rodilla_der']), axis=1)
    dfm["sim_codo"] = dfm.apply(lambda r: calculate_symmetry(r['codo_izq'], r['codo_der']), axis=1)
    return dfm

# =================================================================================
# 3. FUNCIONES PURAS DE UTILIDAD (CÁLCULOS MATEMÁTICOS)
# =================================================================================

def normalize_landmarks(landmarks):
    hip_left = landmarks[23]
    hip_right = landmarks[24]
    cx = (hip_left['x'] + hip_right['x']) / 2.0
    cy = (hip_left['y'] + hip_right['y']) / 2.0
    return [{'x': lm['x'] - cx, 'y': lm['y'] - cy, 'z': lm['z'], 'visibility': lm['visibility']} for lm in landmarks]

def calculate_angle(p1, p2, p3):
    v1 = (p1['x'] - p2['x'], p1['y'] - p2['y'])
    v2 = (p3['x'] - p2['x'], p3['y'] - p2['y'])
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
    magnitude1 = math.hypot(v1[0], v1[1])
    magnitude2 = math.hypot(v2[0], v2[1])
    if magnitude1 * magnitude2 == 0: return 0.0
    cosine_angle = max(min(dot_product / (magnitude1 * magnitude2), 1.0), -1.0)
    return math.degrees(math.acos(cosine_angle))

def extract_joint_angles(landmarks):
    return {
        'rodilla_izq': calculate_angle(landmarks[23], landmarks[25], landmarks[27]),
        'rodilla_der': calculate_angle(landmarks[24], landmarks[26], landmarks[28]),
        'codo_izq': calculate_angle(landmarks[11], landmarks[13], landmarks[15]),
        'codo_der': calculate_angle(landmarks[12], landmarks[14], landmarks[16]),
    }

def calculate_distances(landmarks):
    return {
        'anchura_hombros': abs(landmarks[12]['x'] - landmarks[11]['x']),
        'separacion_pies': abs(landmarks[28]['x'] - landmarks[27]['x']),
    }

def calculate_angular_velocity(angle_sequence, fps):
    if not angle_sequence or fps == 0: return [0.0] * len(angle_sequence)
    velocities = [0.0]  # La velocidad en el primer frame es 0
    dt = 1.0 / fps
    for i in range(1, len(angle_sequence)):
        delta_angle = angle_sequence[i] - angle_sequence[i-1]
        velocities.append(abs(delta_angle) / dt)
    return velocities

def calculate_symmetry(angle_left, angle_right):
    if pd.isna(angle_left) or pd.isna(angle_right): return np.nan
    max_angle = max(abs(angle_left), abs(angle_right))
    if max_angle == 0: return 1.0
    return 1.0 - (abs(angle_left - angle_right) / max_angle)