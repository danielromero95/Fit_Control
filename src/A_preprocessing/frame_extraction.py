# --------------------------------------------------------
# Archivo: frame_extraction.py
# --------------------------------------------------------
"""
Definiciones de extensiones de archivo aceptadas para vídeos e imágenes,
y lógica de extracción + preprocesamiento de fotogramas con logging de depuración.

Ahora cada frame SE REDIMENSIONA y/o SE NORMALIZA antes de guardarlo, 
siguiendo parámetros: target_width, target_height y normalize.
"""

import cv2
import os
import logging

# ---------------------------------
# Configuración básica de logging
# ---------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# --------------------------------------------------------
# src/A_preprocessing/file_extensions.py (inlined aquí)
# --------------------------------------------------------
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".mpg", ".mpeg", ".wmv"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}


# --------------------------------------------------------
# Función de extracción + preprocesamiento de fotogramas
# --------------------------------------------------------
def extract_and_preprocess_frames(
        video_path,
        output_dir,
        sample_rate=3,
        rotate=0,
        target_width=256,
        target_height=256,
        normalize=False
    ):
    """
    Extrae 1 de cada `sample_rate` fotogramas de `video_path`, opcionalmente los rota,
    los redimensiona a (target_width, target_height), normaliza si se pidió, 
    y los guarda en `output_dir`. Devuelve metadata:
    {
        'fps': float,
        'frame_count': int,
        'duration': float (en segundos),
        'frames_saved': int
    }

    Parámetros:
        - video_path    : ruta al archivo de vídeo.
        - output_dir    : directorio donde se guardarán los fotogramas finales.
        - sample_rate   : tomar 1 fotograma de cada N (por defecto: 3).
        - rotate        : grados de rotación (0, 90, 180, 270).
        - target_width  : ancho final de los frames (por defecto: 256).
        - target_height : alto final de los frames (por defecto: 256).
        - normalize     : si es True, convierte el rango de píxel 0–255 a 0.0–1.0 y vuelve a 0–255 para guardarlo.
    """
    logger.debug("Iniciando extracción + preprocesamiento de fotogramas.")
    logger.debug(f"video_path = {video_path}")
    logger.debug(f"output_dir = {output_dir}")
    logger.debug(f"sample_rate = {sample_rate}, rotate = {rotate}")
    logger.debug(f"target_size = {target_width}x{target_height}, normalize = {normalize}")

    # 1) Verificar que la extensión del vídeo sea válida
    ext = os.path.splitext(video_path)[1].lower()
    if ext not in VIDEO_EXTENSIONS:
        msg = f"Extensión de vídeo no soportada: '{ext}'. Se esperan: {sorted(VIDEO_EXTENSIONS)}"
        logger.error(msg)
        raise ValueError(msg)

    # 2) Intentar abrir el vídeo
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        msg = f"No se pudo abrir el vídeo: {video_path}"
        logger.error(msg)
        raise IOError(msg)

    # 3) Obtener propiedades del vídeo
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0.0
    logger.info(f"Propiedades del vídeo: FPS={fps:.2f}, Total fotogramas={frame_count}, Duración={duration:.2f}s")

    # 4) Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    logger.debug(f"Directorio de salida creado o ya existente: {output_dir}")

    idx = 0
    saved = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            logger.debug("No quedan más fotogramas por leer.")
            break

        # Solo procesar cada sample_rate fotograma
        if idx % sample_rate == 0:
            # 5) Aplicar rotación si se pidió
            if rotate == 90:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                logger.debug(f"Rotando 90° en fotograma idx={idx}")
            elif rotate == 180:
                frame = cv2.rotate(frame, cv2.ROTATE_180)
                logger.debug(f"Rotando 180° en fotograma idx={idx}")
            elif rotate == 270:
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                logger.debug(f"Rotando 270° en fotograma idx={idx}")

            # 6) REDIMENSIONAR a (target_width x target_height)
            try:
                frame = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_AREA)
            except Exception as e:
                logger.warning(f"No se pudo redimensionar fotograma idx={idx}: {e}")

            # 7) NORMALIZAR si se pidió: (0–255 → 0.0–1.0 → 0–255)
            if normalize:
                try:
                    frame = frame.astype("float32") / 255.0
                    frame = (frame * 255.0).astype("uint8")
                except Exception as e:
                    logger.warning(f"Problema al normalizar fotograma idx={idx}: {e}")

            # 8) Guardar el frame final en disco
            filename = os.path.join(output_dir, f"frame_{saved+1:04d}.jpg")
            success = cv2.imwrite(filename, frame)
            if success:
                saved += 1
                logger.debug(f"Fotograma procesado guardado: {filename}")
            else:
                logger.warning(f"Error al guardar fotograma: {filename}")

        idx += 1

    cap.release()
    logger.info(
        f"Extracción + preprocesamiento completado: fps={fps:.2f}, frame_count={frame_count}, "
        f"duration={duration:.2f}, frames_saved={saved}"
    )

    return {
        'fps': fps,
        'frame_count': frame_count,
        'duration': duration,
        'frames_saved': saved
    }


# --------------------------------------------------------
# Si se ejecuta por CLI, permitimos parámetros extra de preprocesamiento
# --------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Extrae y preprocesa fotogramas: muestrea, rota, redimensiona y normaliza."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Ruta al vídeo de entrada (ej. data/raw/own_videos/ejemplo.mp4)."
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Directorio donde se guardarán los fotogramas preprocesados."
    )
    parser.add_argument(
        "--sample_rate",
        type=int,
        default=3,
        help="Tomar 1 fotograma de cada N (por defecto: 3)."
    )
    parser.add_argument(
        "--rotate",
        type=int,
        choices=[0, 90, 180, 270],
        default=0,
        help="Rotar cada fotograma (0, 90, 180, 270)."
    )
    parser.add_argument(
        "--width",
        type=int,
        default=256,
        help="Ancho final de los fotogramas (por defecto: 256)."
    )
    parser.add_argument(
        "--height",
        type=int,
        default=256,
        help="Alto final de los fotogramas (por defecto: 256)."
    )
    parser.add_argument(
        "--normalize",
        action="store_true",
        help="Si se incluye, normaliza el rango de píxeles 0–255 → 0.0–1.0 → 0–255."
    )

    args = parser.parse_args()

    try:
        metadata = extract_and_preprocess_frames(
            video_path=args.input,
            output_dir=args.output,
            sample_rate=args.sample_rate,
            rotate=args.rotate,
            target_width=args.width,
            target_height=args.height,
            normalize=args.normalize
        )
        print("----- Resumen de extracción + preprocesamiento -----")
        print(f"FPS del vídeo       : {metadata['fps']:.2f}")
        print(f"Total de fotogramas : {metadata['frame_count']}")
        print(f"Duración (s)        : {metadata['duration']:.2f}")
        print(f"Fotogramas guardados: {metadata['frames_saved']}")
        print(f"Tamaño final        : {args.width}×{args.height}, normalize={args.normalize}")
        print(f"Directorio de salida: {args.output}")
        print("----- Proceso completado -----")
    except Exception as e:
        logger.exception("Falló la extracción + preprocesamiento.")
        exit(1)
