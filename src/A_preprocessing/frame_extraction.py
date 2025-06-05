# src/A_preprocessing/frame_extraction.py

import cv2
import os
import argparse
from src.A_preprocessing.file_extensions import VIDEO_EXTENSIONS  # importar extensiones de video

def extract_frames(video_path, output_dir, sample_rate=3, rotate=0):
    """
    Extrae 1 de cada `sample_rate` fotogramas de `video_path`, opcionalmente los rota,
    y los guarda en `output_dir`. Devuelve metadata:
    {
        'fps': float,
        'frame_count': int,
        'duration': float (en segundos),
        'frames_saved': int
    }
    Parámetros:
        - video_path: ruta al archivo de vídeo.
        - output_dir: directorio donde se guardarán los fotogramas.
        - sample_rate: tomar 1 fotograma de cada N (por defecto: 3).
        - rotate: grados de rotación por fotograma (0, 90, 180, 270).
    """
    # Verificar que la extensión del vídeo sea válida
    ext = os.path.splitext(video_path)[1].lower()
    if ext not in VIDEO_EXTENSIONS:
        raise ValueError(f"Extensión de video no soportada: '{ext}'. "
                         f"Se esperan: {sorted(VIDEO_EXTENSIONS)}")

    # Intentar abrir el vídeo
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"No se pudo abrir el vídeo: {video_path}")

    # Obtener propiedades del vídeo
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0.0

    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)

    idx = 0
    saved = 0

    # Iterar sobre todos los fotogramas
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # Se acabaron los fotogramas

        # Guardar solo cada `sample_rate` fotograma
        if idx % sample_rate == 0:
            # Aplicar rotación si se especificó
            if rotate == 90:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            elif rotate == 180:
                frame = cv2.rotate(frame, cv2.ROTATE_180)
            elif rotate == 270:
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

            # Nombre secuencial basado en la cuenta de guardados
            filename = os.path.join(output_dir, f"frame_{saved+1:04d}.jpg")
            # Guardar el fotograma (en formato BGR por defecto)
            cv2.imwrite(filename, frame)
            saved += 1

        idx += 1

    cap.release()

    return {
        'fps': fps,
        'frame_count': frame_count,
        'duration': duration,
        'frames_saved': saved
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extrae fotogramas muestreando cada N fotogramas y opcionalmente los rota."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Ruta al vídeo de entrada (ej. data/raw/own_videos/1-Squat_Own/Sentadilla_Dani.mp4)."
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Directorio donde se guardarán los fotogramas (ej. data/processed/frames/1-Squat_Own)."
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
        help="Rotar cada fotograma en grados (0, 90, 180, 270). Por defecto: 0."
    )
    args = parser.parse_args()

    # Llamar a la función de extracción con rotación
    metadata = extract_frames(
        video_path=args.input,
        output_dir=args.output,
        sample_rate=args.sample_rate,
        rotate=args.rotate
    )

    # Mostrar resumen de la extracción
    print("----- Resumen de extracción -----")
    print(f"FPS del vídeo       : {metadata['fps']:.2f}")
    print(f"Total de fotogramas : {metadata['frame_count']}")
    print(f"Duración (s)        : {metadata['duration']:.2f}")
    print(f"Fotogramas guardados: {metadata['frames_saved']}")
    print(f"Rotación aplicada   : {args.rotate} grados")
    print(f"Directorio de salida: {args.output}")
    print("----- Extracción completada -----")

