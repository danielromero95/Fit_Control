# src/B_pose_estimation/estimators.py

import cv2
import numpy as np
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict

try:
    import mediapipe as mp
    from mediapipe.python.solutions.pose import Pose
except ImportError:
    logging.error("MediaPipe no está instalado. Por favor, ejecuta 'pip install mediapipe'.")
    raise

logger = logging.getLogger(__name__)


@dataclass
class EstimationResult:
    """
    Contenedor de datos estandarizado para el resultado de una estimación de pose.
    Utiliza tipos de datos simples (listas de dicts) para ser seguro entre procesos.
    """
    landmarks: Optional[List[Dict[str, float]]] = None
    world_landmarks: Optional[List[Dict[str, float]]] = None
    annotated_image: Optional[np.ndarray] = None


class BaseEstimator(ABC):
    """Clase base abstracta para todos los estimadores de pose."""
    @abstractmethod
    def estimate(self, image: np.ndarray) -> EstimationResult:
        """Estima la pose en un único fotograma."""
        raise NotImplementedError

    @abstractmethod
    def close(self):
        """Libera los recursos del modelo."""
        raise NotImplementedError


class BlazePose3DEstimator(BaseEstimator):
    """
    Estimador que utiliza MediaPipe Pose y devuelve los landmarks como listas
    de diccionarios para garantizar la robustez en el multiprocesamiento.
    """
    def __init__(self):
        self.pose = Pose(
            static_image_mode=False,
            model_complexity=2,
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=0.5
        )

    def estimate(self, image: np.ndarray) -> EstimationResult:
        """
        Procesa un frame, extrae los landmarks y los convierte a un formato de datos simple.
        """
        results = self.pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if not results.pose_landmarks:
            return EstimationResult(annotated_image=image)
        
        # Convertimos los objetos complejos de MediaPipe a listas de diccionarios simples
        landmarks_2d = [{'x': lm.x, 'y': lm.y, 'z': lm.z, 'visibility': lm.visibility} 
                        for lm in results.pose_landmarks.landmark]
        
        world_landmarks_3d = [{'x': lm.x, 'y': lm.y, 'z': lm.z, 'visibility': lm.visibility} 
                              for lm in results.pose_world_landmarks.landmark]
        
        # Creamos una imagen anotada para depuración rápida si es necesario
        annotated_image = image.copy()
        mp.solutions.drawing_utils.draw_landmarks(
            annotated_image, 
            results.pose_landmarks, 
            mp.solutions.pose.POSE_CONNECTIONS
        )
        
        return EstimationResult(
            landmarks=landmarks_2d,
            world_landmarks=world_landmarks_3d,
            annotated_image=annotated_image,
        )

    def close(self):
        self.pose.close()


class CroppedPoseEstimator(BaseEstimator):
    """
    Placeholder para el estimador 2D. Necesitaría ser refactorizado de forma
    similar para devolver un objeto EstimationResult si se quisiera usar.
    """
    def estimate(self, image: np.ndarray) -> EstimationResult:
        logger.warning("CroppedPoseEstimator no está completamente implementado con la nueva arquitectura.")
        # Aquí iría la lógica original, adaptada para devolver un EstimationResult
        return EstimationResult(annotated_image=image)

    def close(self):
        pass
