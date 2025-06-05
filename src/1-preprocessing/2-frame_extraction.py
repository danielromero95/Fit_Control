import cv2
import os

def extract_frames(video_path, output_dir, sample_rate=3):
    """
    Extrae 1 de cada `sample_rate` fotogramas de `video_path` y los guarda en `output_dir`.
    Devuelve metadata: { 'fps':..., 'frame_count':..., 'duration':... }
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"No se pudo abrir el vídeo {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps

    os.makedirs(output_dir, exist_ok=True)
    idx = 0
    saved = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % sample_rate == 0:
            filename = os.path.join(output_dir, f"frame_{idx:05d}.jpg")
            # Convertir BGR a RGB si se desea, o guardar tal cual
            cv2.imwrite(filename, frame)
            saved += 1
        idx += 1

    cap.release()
    return {'fps': fps, 'frame_count': frame_count, 'duration': duration, 'frames_saved': saved}
