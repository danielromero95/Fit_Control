import cv2

def validate_video(path):
    """
    Intenta abrir el vídeo en 'path' usando OpenCV.
    Si no se puede abrir, levanta IOError.
    Si se abre correctamente, devuelve un dict con:
      - 'fps': fotogramas por segundo
      - 'frame_count': número total de frames
      - 'duration': duración aproximada en segundos (frame_count / fps)
    """
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        cap.release()
        raise IOError(f"No se pudo abrir el vídeo en: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    if fps == 0:
        # Podría ser un vídeo corrupto o con metadatos vacíos
        raise ValueError(f"FPS = 0. Vídeo posiblemente corrupto: {path}")
    duration = frame_count / fps
    return {
        "fps": fps,
        "frame_count": frame_count,
        "duration": duration
    }
