import mediapipe as mp
import numpy as np
import math

mp_pose = mp.solutions.pose

class PoseEstimator:

    """
    Pruebas unitarias sugeridas:
    - Test con imagen sintética (por ejemplo, un frame de prueba) y verificar que landmarks sea una lista de largo 33 (MediaPipe Pose detecta 33 puntos).
    - Test con imagen vacía o sin persona: landmarks = None.
    """
    def __init__(self, static_image_mode=False, model_complexity=1, min_detection_confidence=0.5):
        self.pose = mp_pose.Pose(static_image_mode=static_image_mode,
                                 model_complexity=model_complexity,
                                 min_detection_confidence=min_detection_confidence)

    def estimate_pose(self, image):
        """
        Recibe `image` en formato RGB, retorna:
        - landmarks: lista de dicts { 'x':..., 'y':..., 'z':..., 'visibility':... }
        - image_out: imagen con landmarks dibujados (opcional)
        """
        results = self.pose.process(image)
        if not results.pose_landmarks:
            return None, image
        landmarks = []
        for lm in results.pose_landmarks.landmark:
            landmarks.append({
                'x': lm.x,
                'y': lm.y,
                'z': lm.z,
                'visibility': lm.visibility
            })
        # Dibujar sobre copia de imagen
        annotated = image.copy()
        mp.solutions.drawing_utils.draw_landmarks(
            annotated, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        return landmarks, annotated

# Filtrar y interpolar secuencia de keypoints
def filter_and_interpolate_keypoints(landmarks_sequence, min_confidence=0.5):
    """
    Recibe una lista de lista de landmarks por fotograma:
    landmarks_sequence = [landmarks_t0, landmarks_t1, ..., landmarks_tN]
    Cada landmarks_t es lista de dicts o None.
    Retorna:
    - secuencia_filtrada: misma estructura, con puntos interpolados o None.
    """
    n_frames = len(landmarks_sequence)
    n_points = 33  # número de keypoints de MediaPipe Pose
    # Inicializar array: shape (n_frames, n_points, 3) -> (x,y,visibility)
    arr = np.zeros((n_frames, n_points, 3), dtype=float)
    valid = np.zeros((n_frames, n_points), dtype=bool)
    for t, lm in enumerate(landmarks_sequence):
        if lm is None:
            continue
        for i, point in enumerate(lm):
            if point['visibility'] >= min_confidence:
                arr[t, i, 0] = point['x']
                arr[t, i, 1] = point['y']
                arr[t, i, 2] = point['visibility']
                valid[t, i] = True
    # Interpolación en tiempo para cada punto
    for i in range(n_points):
        valid_indices = np.where(valid[:, i])[0]
        if len(valid_indices) == 0:
            continue
        # Interpolación lineal para x,y separadamente
        for dim in [0,1]:
            arr[:, i, dim] = np.interp(
                np.arange(n_frames),
                valid_indices,
                arr[valid_indices, i, dim]
            )
        # Marcar visibilidad interpolada como 1
        arr[~valid[:, i], i, 2] = 0.0  # visibility bajo confianza
    # Construir secuencia filtrada
    filtered_seq = []
    for t in range(n_frames):
        points = []
        count_low = 0
        for i in range(n_points):
            vis = arr[t, i, 2]
            if vis < min_confidence:
                count_low += 1
            points.append({'x': arr[t, i, 0], 'y': arr[t, i, 1], 'visibility': vis})
        # Si hay más del 20% de puntos con vis < min_confidence, descartar fotograma
        if count_low / n_points > 0.2:
            filtered_seq.append(None)
        else:
            filtered_seq.append(points)
    return filtered_seq

# Normalizar keypoints centrados en caderas
def normalize_landmarks(landmarks, image_width, image_height):
    """
    Recibe una lista de keypoints {x, y, visibility} normalizados en [0,1] sobre imagen.
    Centra el sistema en el punto medio de cadera ((x_izq + x_der)/2, (y_izq + y_der)/2).
    Retorna una lista de vectores normalizados.
    """
    # Indices de cadera en MediaPipe:  
    # 23 = cadera izquierda, 24 = cadera derecha
    hip_left = landmarks[23]
    hip_right = landmarks[24]
    cx = (hip_left['x'] + hip_right['x']) / 2
    cy = (hip_left['y'] + hip_right['y']) / 2
    normalized = []
    for lm in landmarks:
        nx = (lm['x'] - cx)  # ya en [–1,1] aprox.
        ny = (lm['y'] - cy)
        normalized.append({'x': nx, 'y': ny, 'visibility': lm['visibility']})
    return normalized


def calculate_angle(p1, p2, p3):
    """
    Calcula ángulo (en grados) formado en p2 por p1-p2-p3. 
    Cada punto es dict {'x':..., 'y':...}.
    """
    v1 = (p1['x'] - p2['x'], p1['y'] - p2['y'])
    v2 = (p3['x'] - p2['x'], p3['y'] - p2['y'])
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    mag1 = math.hypot(v1[0], v1[1])
    mag2 = math.hypot(v2[0], v2[1])
    if mag1 == 0 or mag2 == 0:
        return 0.0
    cos_angle = max(min(dot / (mag1 * mag2), 1.0), -1.0)
    angle = math.degrees(math.acos(cos_angle))
    return angle

def extract_joint_angles(normalized_landmarks):
    """
    Dado lista de 33 landmarks normalizados, calcula ángulos relevantes:
    - Rodilla (cadera-rodilla-tobillo) para ambas piernas.
    - Codo (hombro-codo-muñeca) para ambos brazos.
    Retorna diccionario de ángulos, e.g.: 
    { 'rodilla_izq': θ, 'rodilla_der': θ, 'codo_izq': θ, 'codo_der': θ }
    """
    # Indices según MediaPipe:
    # Hombros: 11 (izq), 12 (der)
    # Codos: 13 (izq), 14 (der)
    # Muñecas: 15 (izq), 16 (der)
    # Caderas: 23 (izq), 24 (der)
    # Rodillas: 25 (izq), 26 (der)
    # Tobillos: 27 (izq), 28 (der)

    angles = {}
    # Rodilla izquierda
    angles['rodilla_izq'] = calculate_angle(
        normalized_landmarks[23], normalized_landmarks[25], normalized_landmarks[27]
    )
    # Rodilla derecha
    angles['rodilla_der'] = calculate_angle(
        normalized_landmarks[24], normalized_landmarks[26], normalized_landmarks[28]
    )
    # Codo izquierdo
    angles['codo_izq'] = calculate_angle(
        normalized_landmarks[11], normalized_landmarks[13], normalized_landmarks[15]
    )
    # Codo derecho
    angles['codo_der'] = calculate_angle(
        normalized_landmarks[12], normalized_landmarks[14], normalized_landmarks[16]
    )
    return angles

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Cálculo de distancias entre puntos clave
def calculate_distances(normalized_landmarks):
    """
    Calcula distancias en coordenadas normalizadas:
    - Anchura hombros: |x12 - x11|
    - Separación pies: |x28 - x27|
    Retorna un diccionario: { 'anchura_hombros': ..., 'separacion_pies': ... }
    """
    # Hombros: 11 izq, 12 der
    # Tobillos: 27 izq, 28 der
    ancho_hombros = abs(normalized_landmarks[12]['x'] - normalized_landmarks[11]['x'])
    separacion_pies = abs(normalized_landmarks[28]['x'] - normalized_landmarks[27]['x'])
    return {'anchura_hombros': ancho_hombros, 'separacion_pies': separacion_pies}

# Cálculo de velocidad angular
def calculate_angular_velocity(angle_sequence, fps):
    """
    Recibe lista de ángulos por fotograma (en grados) y fps.
    Retorna lista de velocidades angulares por fotograma (en grados/seg).
    """
    velocities = []
    dt = 1.0 / fps
    for i in range(1, len(angle_sequence)):
        velocities.append(abs(angle_sequence[i] - angle_sequence[i-1]) / dt)
    # La primera velocidad se asume igual a la segunda o 0
    return [velocities[0]] + velocities

# Cálculo de simetría entre ángulos de extremidades
def calculate_symmetry(angle_left, angle_right):
    """
    Calcula simetría entre ángulos izquierdo y derecho:
    sim = 1 - |θizq - θder| / max(θizq, θder)
    Si ambos son 0, se define sim = 1.
    """
    if max(angle_left, angle_right) == 0:
        return 1.0
    return 1.0 - abs(angle_left - angle_right) / max(angle_left, angle_right)
