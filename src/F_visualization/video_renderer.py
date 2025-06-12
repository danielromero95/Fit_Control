# src/F_visualization/video_renderer.py

import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

def render_landmarks_on_video(
    original_frames: list,
    landmarks_sequence: np.ndarray,
    output_path: str,
    fps: float
):
    """
    Dibuja una secuencia de landmarks sobre una secuencia de fotogramas y
    guarda el resultado como un nuevo vídeo.

    Args:
        original_frames (list): Lista de fotogramas originales (arrays de NumPy BGR).
        landmarks_sequence (np.ndarray): Array de secuencias de landmarks, donde cada
                                         elemento es una lista de 33 dicts de landmark.
        output_path (str): Ruta donde se guardará el vídeo de salida (ej. 'debug.mp4').
        fps (float): Fotogramas por segundo del vídeo de salida.
    """
    logger.info(f"Iniciando renderizado de vídeo de depuración en: {output_path}")

    # Intentamos importar las utilidades de MediaPipe de forma segura
    try:
        from mediapipe.python.solutions import drawing_utils as mp_drawing
        from mediapipe.python.solutions import pose as mp_pose
        from mediapipe.framework.formats import landmark_pb2
    except ImportError:
        logger.error("MediaPipe no está instalado. No se puede renderizar el vídeo de depuración.")
        return

    if not original_frames:
        logger.warning("No hay fotogramas para renderizar.")
        return

    # Definir el codec y crear el objeto VideoWriter
    height, width, _ = original_frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec para .mp4
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    if not writer.isOpened():
        logger.error(f"No se pudo abrir VideoWriter para la ruta: {output_path}")
        return

    # Iterar sobre cada fotograma y sus landmarks correspondientes
    for frame_idx, frame in enumerate(original_frames):
        annotated_frame = frame.copy()
        
        if frame_idx < len(landmarks_sequence) and landmarks_sequence[frame_idx] is not None:
            frame_landmarks = landmarks_sequence[frame_idx]
            
            # Convertir nuestra lista de dicts de Python al formato protobuf que MediaPipe necesita
            landmark_proto_list = landmark_pb2.NormalizedLandmarkList()
            for lm_dict in frame_landmarks:
                if not np.isnan(lm_dict['x']):
                    landmark_proto_list.landmark.add(
                        x=lm_dict['x'], y=lm_dict['y'], z=lm_dict['z'], visibility=lm_dict['visibility']
                    )

            # Dibujar el esqueleto
            mp_drawing.draw_landmarks(
                image=annotated_frame,
                landmark_list=landmark_proto_list,
                connections=mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2),
                connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2)
            )
        
        # Escribir el fotograma anotado en el vídeo de salida
        writer.write(annotated_frame)

    writer.release()
    logger.info("Vídeo de depuración renderizado con éxito.")