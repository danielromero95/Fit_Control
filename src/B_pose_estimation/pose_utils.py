# src/B_pose_estimation/pose_utils.py

import os
import cv2
import numpy as np
import math
import argparse
import pandas as pd

# src/B_pose_estimation/pose_utils.py (parte superior)

import os
import cv2
import numpy as np
import math
import argparse
import pandas as pd

# ---------------------------------------------------------------------------------
# 1. CLASE PoseEstimator (importa mediapipe SOLO si se instancia)
# ---------------------------------------------------------------------------------
class PoseEstimator:
    """
    Encapsula MediaPipe Pose (sin cropping).
    La importación de MediaPipe se hace en el constructor, para que
    si nunca se usa este objeto (e.g. en filter_interp/metrics), no falle.
    """
    def __init__(self, static_image_mode=False, model_complexity=1, min_detection_confidence=0.5):
        # Importamos aquí para no exigir mediapipe si nunca se usa este constructor:
        from mediapipe.python.solutions import pose as mp_pose_module
        from mediapipe.python.solutions import drawing_utils as mp_drawing_utils

        self.mp_pose_module = mp_pose_module
        self.mp_drawing_utils = mp_drawing_utils

        # Creamos el objeto Pose
        self.pose = self.mp_pose_module.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence
        )

    def estimate_pose(self, image):
        """
        Recibe `image` en formato BGR (OpenCV), retorna:
          - landmarks: lista de 33 dicts {'x','y','z','visibility'} o None si no detecta.
          - annotated_image: copia de imagen con landmarks dibujados (BGR).
        """
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(img_rgb)

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

        annotated = image.copy()
        self.mp_drawing_utils.draw_landmarks(
            annotated,
            results.pose_landmarks,
            self.mp_pose_module.POSE_CONNECTIONS
        )
        return landmarks, annotated

    def close(self):
        self.pose.close()


# ---------------------------------------------------------------------------------
# 1. CLASE CroppedPoseEstimator (importa mediapipe SOLO si se instancia)
# ---------------------------------------------------------------------------------
#
# Este wrapper hace dos pasadas:
#   1) Detecta pose en la imagen entera para obtener landmarks.
#   2) Crea un recuadro (crop) en torno a esos landmarks, redimensiona y re-detecta pose
#      en el recorte, para obtener landmarks “centrados”.
#
# Devolvemos:
#   - landmarks_crop: lista de 33 dicts {'x','y','z','visibility'}, en coordenadas
#                      RELATIVAS al recorte (normalizadas en [0,1] dado el nuevo tamaño).
#   - annotated_crop: la imagen recortada (en BGR) con los landmarks dibujados sobre ella.
#
class CroppedPoseEstimator:
    def __init__(self,
                 static_image_mode=False,
                 model_complexity=1,
                 min_detection_confidence=0.5,
                 crop_margin=0.15,
                 target_size=(256, 256)):
        """
        crop_margin: porcentaje extra que se añade al bounding-box (p. ej. 0.15 → 15% de margen).
        target_size: tamaño final del recorte (width, height), p. ej. (256,256).
        """
        self.crop_margin = crop_margin
        self.target_size = target_size  # (ancho, alto) del recorte final

        # Importamos MediaPipe aquí para no exigirlo si nunca se instancia este objeto
        from mediapipe.python.solutions import pose as mp_pose_module
        from mediapipe.python.solutions import drawing_utils as mp_drawing_utils

        # Guardamos referencias al módulo y utilidades de dibujo
        self.mp_pose_module = mp_pose_module
        self.mp_drawing_utils = mp_drawing_utils

        # Creamos dos instancias de Pose:
        #  - Una para detectar en la imagen completa (pose_full)
        #  - Otra para detectar en el recorte redimensionado (pose_crop)
        self.pose_full = self.mp_pose_module.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence
        )
        self.pose_crop = self.mp_pose_module.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence
        )

    def estimate_and_crop(self, image_bgr):
        """
        1) Detecta pose en toda la imagen → obtiene landmarks_full (normalizados).
        2) Si no hay landmarks, retorna (None, image_bgr).
        3) Convierte landmarks_full a coordenadas en píxeles.
        4) Construye bounding-box (BB) con margen y recorta la región que contiene la persona.
        5) Redimensiona el recorte a self.target_size y vuelve a estimar pose en el recorte.
        6) Retorna (landmarks_crop, annotated_crop):
           - landmarks_crop: lista de 33 dicts {'x','y','z','visibility'} normalizados en [0,1] relativos al recorte.
           - annotated_crop: imagen recortada (target_size) en BGR con los landmarks dibujados.
        """
        h0, w0 = image_bgr.shape[:2]

        # ------------------- PASO 1: detectar pose en toda la imagen -------------------
        img_rgb_full = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        results_full = self.pose_full.process(img_rgb_full)
        if not results_full.pose_landmarks:
            # Si no detecta persona, devolvemos None para landmarks y la imagen entera sin modificación
            return None, image_bgr

        # ---------------- PASO 2: convertir landmarks normalizados en pixeles ----------------
        lms_full = results_full.pose_landmarks.landmark  # lista de 33 landmarks
        # Array de forma (33, 2): [(x0_pix, y0_pix), (x1_pix, y1_pix), ...]
        xy_full = np.array([[lm.x * w0, lm.y * h0] for lm in lms_full])

        # ---------------- PASO 3: construir bounding-box mínimo que encierra todos los puntos ----------------
        x_min, y_min = xy_full.min(axis=0)
        x_max, y_max = xy_full.max(axis=0)

        # Añadimos un poco de margen (% del ancho/alto del BB) para no recortar demasiado justo
        dx = (x_max - x_min) * self.crop_margin
        dy = (y_max - y_min) * self.crop_margin

        # Clamp al rango de la imagen original
        x1 = max(int(x_min - dx), 0)
        y1 = max(int(y_min - dy), 0)
        x2 = min(int(x_max + dx), w0 - 1)
        y2 = min(int(y_max + dy), h0 - 1)

        # --------------------- PASO 4: recortar la región que contiene la persona ---------------------
        crop = image_bgr[y1:y2, x1:x2]  # subimagen en BGR
        if crop.size == 0:
            # En caso extremo (BB inválido), devolvemos la imagen completa sin crop
            return None, image_bgr

        # ---------------- PASO 5: redimensionar el recorte y volver a estimar pose allí ----------------
        w_tgt, h_tgt = self.target_size
        crop_resized = cv2.resize(crop, (w_tgt, h_tgt), interpolation=cv2.INTER_LINEAR)
        crop_rgb = cv2.cvtColor(crop_resized, cv2.COLOR_BGR2RGB)
        results_crop = self.pose_crop.process(crop_rgb)

        landmarks_crop = []
        annotated_crop = crop_resized.copy()

        if results_crop.pose_landmarks:
            # Recojo los landmarks normalizados (0..1) relativos al crop_redimensionado
            for lm in results_crop.pose_landmarks.landmark:
                landmarks_crop.append({
                    'x': lm.x,
                    'y': lm.y,
                    'z': lm.z,
                    'visibility': lm.visibility
                })
            # Dibujar los landmarks sobre la copia del recorte
            self.mp_drawing_utils.draw_landmarks(
                annotated_crop,
                results_crop.pose_landmarks,
                self.mp_pose_module.POSE_CONNECTIONS
            )
        else:
            # Si no detecta pose en el recorte, devolvemos landmarks_crop=None y el recorte sin marcar
            landmarks_crop = None

        return landmarks_crop, annotated_crop

    def close(self):
        self.pose_full.close()
        self.pose_crop.close()



# ---------------------------------------------------------------------------------
# 2. FILTRADO E INTERPOLACIÓN
# ---------------------------------------------------------------------------------
def filter_and_interpolate_keypoints(landmarks_sequence, min_confidence=0.5):
    """
    Recibe una lista de lista de landmarks por fotograma:
    landmarks_sequence = [landmarks_t0, landmarks_t1, ..., landmarks_tN]
    Cada landmarks_t es lista de dicts o None.
    Retorna:
      - secuencia_filtrada: misma estructura, con puntos interpolados o None.
    """
    n_frames = len(landmarks_sequence)
    n_points = 33
    arr = np.zeros((n_frames, n_points, 3), dtype=float)  # x, y, visibility
    valid = np.zeros((n_frames, n_points), dtype=bool)

    for t, lm in enumerate(landmarks_sequence):
        if lm is None:
            continue
        for i, pt in enumerate(lm):
            if pt['visibility'] >= min_confidence:
                arr[t, i, 0] = pt['x']
                arr[t, i, 1] = pt['y']
                arr[t, i, 2] = pt['visibility']
                valid[t, i] = True

    for i in range(n_points):
        valid_idx = np.where(valid[:, i])[0]
        if len(valid_idx) == 0:
            continue
        arr[:, i, 0] = np.interp(np.arange(n_frames), valid_idx, arr[valid_idx, i, 0])
        arr[:, i, 1] = np.interp(np.arange(n_frames), valid_idx, arr[valid_idx, i, 1])
        arr[~valid[:, i], i, 2] = 0.0  # visibilidad interpolada = 0 en puntos no válidos

    filtered_seq = []
    for t in range(n_frames):
        count_low = np.sum(arr[t, :, 2] < min_confidence)
        if count_low / n_points > 0.2:
            filtered_seq.append(None)
        else:
            pts = []
            for i in range(n_points):
                pts.append({
                    'x': arr[t, i, 0],
                    'y': arr[t, i, 1],
                    'visibility': arr[t, i, 2]
                })
            filtered_seq.append(pts)
    return filtered_seq


# ---------------------------------------------------------------------------------
# 3. NORMALIZACIÓN (CENTRADO EN CADERA)
# ---------------------------------------------------------------------------------
def normalize_landmarks(landmarks):
    """
    Recibe lista de 33 keypoints {'x','y','visibility'} normalizados en [0,1].
    Centra en el punto medio de cadera ((x_izq + x_der)/2, (y_izq + y_der)/2).
    Retorna lista de dicts {'x','y','visibility'} normalizados.
    """
    hip_left = landmarks[23]
    hip_right = landmarks[24]
    cx = (hip_left['x'] + hip_right['x']) / 2
    cy = (hip_left['y'] + hip_right['y']) / 2

    normalized = []
    for lm in landmarks:
        normalized.append({
            'x': lm['x'] - cx,
            'y': lm['y'] - cy,
            'visibility': lm['visibility']
        })
    return normalized


# ---------------------------------------------------------------------------------
# 4. CÁLCULO DE ÁNGULOS DE ARTICULACIONES
# ---------------------------------------------------------------------------------
def calculate_angle(p1, p2, p3):
    """
    Calcula ángulo (en grados) formado en p2 por p1-p2-p3.
    Cada punto es dict {'x','y'}.
    """
    v1 = (p1['x'] - p2['x'], p1['y'] - p2['y'])
    v2 = (p3['x'] - p2['x'], p3['y'] - p2['y'])
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    mag1 = math.hypot(v1[0], v1[1])
    mag2 = math.hypot(v2[0], v2[1])
    if mag1 == 0 or mag2 == 0:
        return 0.0
    cos_ang = max(min(dot / (mag1 * mag2), 1.0), -1.0)
    return math.degrees(math.acos(cos_ang))


def extract_joint_angles(normalized_landmarks):
    """
    Dado lista de 33 landmarks normalizados, calcula ángulos relevantes:
      - Rodilla (cadera-rodilla-tobillo) para ambas piernas.
      - Codo (hombro-codo-muñeca) para ambos brazos.
    Retorna diccionario: { 'rodilla_izq':…, 'rodilla_der':…, 'codo_izq':…, 'codo_der':… }
    """
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


# ---------------------------------------------------------------------------------
# 5. CÁLCULO DE DISTANCIAS Y VELOCIDAD ANGULAR
# ---------------------------------------------------------------------------------
def calculate_distances(normalized_landmarks):
    """
    Calcula distancias en coordenadas normalizadas:
      - Anchura hombros: |x12 - x11|
      - Separación pies: |x28 - x27|
    Retorna diccionario {'anchura_hombros':…, 'separacion_pies':…}.
    """
    ancho_hombros = abs(normalized_landmarks[12]['x'] - normalized_landmarks[11]['x'])
    separacion_pies = abs(normalized_landmarks[28]['x'] - normalized_landmarks[27]['x'])
    return {'anchura_hombros': ancho_hombros, 'separacion_pies': separacion_pies}


def calculate_angular_velocity(angle_sequence, fps):
    """
    Recibe lista de ángulos por fotograma (en grados) y fps.
    Retorna lista de velocidades angulares por fotograma (grados/seg).
    """
    velocities = []
    dt = 1.0 / fps
    for i in range(1, len(angle_sequence)):
        velocities.append(abs(angle_sequence[i] - angle_sequence[i - 1]) / dt)
    if not velocities:
        return []
    return [velocities[0]] + velocities


def calculate_symmetry(angle_left, angle_right):
    """
    Calcula simetría entre ángulos izquierdo y derecho:
      sim = 1 - |θizq - θder| / max(θizq, θder)
    Si ambos son 0, sim = 1.
    """
    if max(angle_left, angle_right) == 0:
        return 1.0
    return 1.0 - abs(angle_left - angle_right) / max(angle_left, angle_right)

# ---------------------------------------------------------------------------------
# 6.1 EXTRACCIÓN POR LOTE A CSV (subcomando "to_csv"), USANDO PoseEstimator (SIN CROP)
# ---------------------------------------------------------------------------------
def extract_pose_landmarks_to_csv_sin_CROP(image_dir, output_csv, visibility_threshold=0.5):
    """
    Usa PoseEstimator para detectar landmarks en cada imagen de image_dir
    y guarda un CSV con columnas:
      image, x0,y0,z0,v0, x1,y1,z1,v1, …, x32,y32,z32,v32.

    (No se hace crop; se procesan los frames completos.)
    """
    estimator = PoseEstimator(
        static_image_mode=True,
        model_complexity=1,
        min_detection_confidence=visibility_threshold
    )

    if not os.path.isdir(image_dir):
        raise NotADirectoryError(f"El directorio no existe: {image_dir}")

    image_files = sorted([f for f in os.listdir(image_dir) if f.lower().endswith(".jpg")])
    rows = []

    for img_name in image_files:
        img_path = os.path.join(image_dir, img_name)
        img = cv2.imread(img_path)
        if img is None:
            print(f"[WARNING] No se pudo leer {img_path}")
            continue

        # Llamamos al PoseEstimator sobre la imagen completa
        landmarks, _ = estimator.estimate_pose(img)

        row = {"image": img_name}
        if landmarks:
            for idx, pt in enumerate(landmarks):
                v = pt['visibility']
                if v < visibility_threshold or math.isnan(v):
                    row[f"x{idx}"] = float("nan")
                    row[f"y{idx}"] = float("nan")
                    row[f"z{idx}"] = float("nan")
                    row[f"v{idx}"] = float("nan")
                else:
                    row[f"x{idx}"] = pt['x']
                    row[f"y{idx}"] = pt['y']
                    row[f"z{idx}"] = pt['z']
                    row[f"v{idx}"] = v
        else:
            # Si no detectó pose, rellenamos todo con NaN:
            for idx in range(33):
                row[f"x{idx}"] = float("nan")
                row[f"y{idx}"] = float("nan")
                row[f"z{idx}"] = float("nan")
                row[f"v{idx}"] = float("nan")

        rows.append(row)

    estimator.close()

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"CSV de landmarks guardado en: {output_csv}")



# ---------------------------------------------------------------------------------
# 6.2 EXTRACCIÓN POR LOTE A CSV (subcomando "to_csv"), USANDO CroppedPoseEstimator
# ---------------------------------------------------------------------------------
def extract_pose_landmarks_to_csv_con_CROP(image_dir, output_csv, visibility_threshold=0.5):
    """
    Usa CroppedPoseEstimator para detectar landmarks en cada imagen de image_dir
    y guarda un CSV con columnas:
      image, x0,y0,z0,v0, x1,y1,z1,v1, …, x32,y32,z32,v32.

    NOTA: ahora el detector se hace “en crop” centrado en la persona, gracias a
    CroppedPoseEstimator. Aunque internamente el wrapper primero detecta en la
    imagen completa y luego recorta, al usuario final le basta con llamar aquí.
    """
    # Importamos CroppedPoseEstimator (definido más arriba en este mismo archivo)
    estimator = CroppedPoseEstimator(
        static_image_mode=True,
        model_complexity=1,
        min_detection_confidence=visibility_threshold,
        crop_margin=0.15,
        target_size=(256, 256)
    )

    if not os.path.isdir(image_dir):
        raise NotADirectoryError(f"El directorio no existe: {image_dir}")

    image_files = sorted([f for f in os.listdir(image_dir) if f.lower().endswith(".jpg")])
    rows = []

    idx_frame = 0  # contador de imágenes para guardar los primeros 2 crops de depuración
    for img_name in image_files:
        img_path = os.path.join(image_dir, img_name)
        img = cv2.imread(img_path)
        if img is None:
            print(f"[WARNING] No se pudo leer {img_path}")
            continue

        # Detectamos y recortamos
        landmarks, annotated_crop = estimator.estimate_and_crop(img)

        # Guardamos los dos primeros crops para depuración
        if idx_frame < 2 and annotated_crop is not None:
            os.makedirs("debug_crops", exist_ok=True)
            cv2.imwrite(os.path.join("debug_crops", f"crop_{idx_frame:03d}.jpg"), annotated_crop)
        idx_frame += 1

        # Empezamos a construir la fila del CSV
        row = {"image": img_name}
        if landmarks:
            # Recorremos cada punto con i (no usamos idx para no pisar idx_frame)
            for i, pt in enumerate(landmarks):
                v = pt['visibility']
                # Si visibilidad baja o NaN, guardamos NaN
                if v < visibility_threshold or math.isnan(v):
                    row[f"x{i}"] = float("nan")
                    row[f"y{i}"] = float("nan")
                    row[f"z{i}"] = float("nan")
                    row[f"v{i}"] = float("nan")
                else:
                    row[f"x{i}"] = pt['x']
                    row[f"y{i}"] = pt['y']
                    row[f"z{i}"] = pt['z']
                    row[f"v{i}"] = v
        else:
            # Si no hubo detección en el crop, rellenamos con NaN para los 33 puntos
            for i in range(33):
                row[f"x{i}"] = float("nan")
                row[f"y{i}"] = float("nan")
                row[f"z{i}"] = float("nan")
                row[f"v{i}"] = float("nan")

        rows.append(row)

    estimator.close()

    # Creamos el DataFrame y lo guardamos
    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"CSV de landmarks guardado en: {output_csv}")



# ---------------------------------------------------------------------------------
# 7. FILTRAR + INTERPOLAR (subcomando "filter_interp")
# ---------------------------------------------------------------------------------
def filter_interp_subcommand(args):
    df = pd.read_csv(args.input_csv)
    frames = sorted(df["image"].unique())
    landmarks_sequence = []

    for img_name in frames:
        row = df[df["image"] == img_name].iloc[0]
        pts = []
        nan_count = 0
        for i in range(33):
            v = row[f"v{i}"]
            if pd.isna(v) or v < args.min_confidence:
                nan_count += 1
                pts.append({'x': 0.0, 'y': 0.0, 'visibility': 0.0})
            else:
                pts.append({'x': row[f"x{i}"], 'y': row[f"y{i}"], 'visibility': v})
        if nan_count / 33 > 0.2:
            landmarks_sequence.append(None)
        else:
            landmarks_sequence.append(pts)

    filtered = filter_and_interpolate_keypoints(landmarks_sequence, min_confidence=args.min_confidence)

    # Convertimos la lista 'filtered' en un array de dtype=object
    filtered_array = np.array(filtered, dtype=object)

    # Nos aseguramos de que el directorio de salida existe
    os.makedirs(os.path.dirname(args.output_npy), exist_ok=True)

    # Guardamos el array de objetos
    np.save(args.output_npy, filtered_array)
    print(f"Secuencia filtrada/interpolada guardada en: {args.output_npy}")


# ---------------------------------------------------------------------------------
# 8. CALCULAR MÉTRICAS (subcomando "metrics")
# ---------------------------------------------------------------------------------
def metrics_subcommand(args):
    seq = np.load(args.input_npy, allow_pickle=True)
    all_metrics = []

    for idx, lm in enumerate(seq):
        row = {"frame_idx": idx}
        if lm is None:
            row.update({
                'rodilla_izq': float("nan"),
                'rodilla_der': float("nan"),
                'codo_izq': float("nan"),
                'codo_der': float("nan"),
                'anchura_hombros': float("nan"),
                'separacion_pies': float("nan"),
            })
        else:
            norm = normalize_landmarks(lm)
            angles = extract_joint_angles(norm)
            dists = calculate_distances(norm)
            row.update(angles)
            row.update(dists)
        all_metrics.append(row)

    dfm = pd.DataFrame(all_metrics)

    rod_izq_seq = dfm["rodilla_izq"].fillna(0).tolist()
    rod_der_seq = dfm["rodilla_der"].fillna(0).tolist()
    codo_izq_seq = dfm["codo_izq"].fillna(0).tolist()
    codo_der_seq = dfm["codo_der"].fillna(0).tolist()

    vel_rod_izq = calculate_angular_velocity(rod_izq_seq, args.fps)
    vel_rod_der = calculate_angular_velocity(rod_der_seq, args.fps)
    vel_codo_izq = calculate_angular_velocity(codo_izq_seq, args.fps)
    vel_codo_der = calculate_angular_velocity(codo_der_seq, args.fps)

    dfm["vel_ang_rod_izq"] = vel_rod_izq
    dfm["vel_ang_rod_der"] = vel_rod_der
    dfm["vel_ang_codo_izq"] = vel_codo_izq
    dfm["vel_ang_codo_der"] = vel_codo_der

    sim_rod = [calculate_symmetry(a, b) for a, b in zip(rod_izq_seq, rod_der_seq)]
    sim_codo = [calculate_symmetry(a, b) for a, b in zip(codo_izq_seq, codo_der_seq)]
    dfm["sim_rodilla"] = sim_rod
    dfm["sim_codo"]    = sim_codo

    os.makedirs(os.path.dirname(args.output_metrics), exist_ok=True)
    dfm.to_csv(args.output_metrics, index=False)
    print(f"Métricas calculadas y guardadas en: {args.output_metrics}")


# ---------------------------------------------------------------------------------
# 9. CLI CON SUBCOMANDOS
# ---------------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extrae landmarks de pose (centrado), filtra, normaliza y calcula métricas."
    )
    subparsers = parser.add_subparsers(dest="command")

    # a) Subcomando: exportar raw landmarks a CSV (ahora centrado en tu cuerpo)
    parser_csv = subparsers.add_parser("to_csv", help="Extraer landmarks raw a CSV (centrado en persona)")
    parser_csv.add_argument("--input_dir", required=True, help="Dir con imágenes (.jpg)")
    parser_csv.add_argument("--output_csv", required=True, help="Ruta al CSV de salida")
    parser_csv.add_argument("--visibility_threshold", type=float, default=0.5)

    # b) Subcomando: filtrar e interpolar landmarks desde CSV existente
    parser_filter = subparsers.add_parser("filter_interp", help="Filtrar e interpolar landmarks desde CSV")
    parser_filter.add_argument("--input_csv", required=True, help="CSV con raw landmarks")
    parser_filter.add_argument("--output_npy", required=True, help="Guardar secuencia filtrada en .npy")
    parser_filter.add_argument("--min_confidence", type=float, default=0.5)

    # c) Subcomando: calcular ángulos y distancias desde secuencia normalizada
    parser_metrics = subparsers.add_parser("metrics", help="Calcular ángulos/distancias desde secuencia normalizada")
    parser_metrics.add_argument("--input_npy", required=True, help="Secuencia filtrada (.npy)")
    parser_metrics.add_argument("--output_metrics", required=True, help="CSV con métricas por frame")
    parser_metrics.add_argument("--fps", type=float, required=True, help="FPS del vídeo original")

    args = parser.parse_args()

    if args.command == "to_csv":
        extract_pose_landmarks_to_csv_sin_CROP(
            image_dir=args.input_dir,
            output_csv=args.output_csv,
            visibility_threshold=args.visibility_threshold
        )

    elif args.command == "filter_interp":
        filter_interp_subcommand(args)

    elif args.command == "metrics":
        metrics_subcommand(args)

    else:
        parser.print_help()

