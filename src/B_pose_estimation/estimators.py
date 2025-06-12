# src/B_pose_estimation/estimators.py
"""
Contiene las clases que encapsulan los modelos de MediaPipe Pose.
Responsabilidad: interactuar directamente con el modelo de IA.
"""
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class PoseEstimator:
    """Encapsula MediaPipe Pose (sin cropping)."""
    def __init__(self, static_image_mode=True, model_complexity=1, min_detection_confidence=0.5):
        try:
            from mediapipe.python.solutions import pose as mp_pose_module, drawing_utils as mp_drawing
        except ImportError:
            logger.error("MediaPipe no está instalado.")
            raise
        self.mp_pose, self.mp_drawing = mp_pose_module, mp_drawing
        self.pose = self.mp_pose.Pose(static_image_mode=static_image_mode, model_complexity=model_complexity, min_detection_confidence=min_detection_confidence)

    def estimate(self, image):
        """Estima la pose y devuelve landmarks y la imagen anotada."""
        results = self.pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.pose_landmarks:
            return None, image
        landmarks = [{'x': lm.x, 'y': lm.y, 'z': lm.z, 'visibility': lm.visibility} for lm in results.pose_landmarks.landmark]
        annotated_image = image.copy()
        self.mp_drawing.draw_landmarks(annotated_image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        return landmarks, annotated_image

    def close(self):
        self.pose.close()

class CroppedPoseEstimator:
    """Wrapper de MediaPipe que realiza una detección en dos pasadas (cropping)."""
    def __init__(self, static_image_mode=True, model_complexity=1, min_detection_confidence=0.5, crop_margin=0.15, target_size=(256, 256)):
        self.crop_margin, self.target_size = crop_margin, target_size
        try:
            from mediapipe.python.solutions import pose as mp_pose_module, drawing_utils as mp_drawing
        except ImportError:
            logger.error("MediaPipe no está instalado.")
            raise
        self.mp_pose, self.mp_drawing = mp_pose_module, mp_drawing
        self.pose_full = self.mp_pose.Pose(static_image_mode=static_image_mode, model_complexity=model_complexity, min_detection_confidence=min_detection_confidence)
        self.pose_crop = self.mp_pose.Pose(static_image_mode=static_image_mode, model_complexity=model_complexity, min_detection_confidence=min_detection_confidence)

    def estimate(self, image_bgr):
        """Detecta, recorta y vuelve a detectar. Devuelve landmarks, imagen anotada y bounding box."""
        h0, w0 = image_bgr.shape[:2]
        results_full = self.pose_full.process(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB))
        if not results_full.pose_landmarks:
            return None, image_bgr, None

        xy_full = np.array([[lm.x * w0, lm.y * h0] for lm in results_full.pose_landmarks.landmark])
        x_min, y_min, x_max, y_max = xy_full[:, 0].min(), xy_full[:, 1].min(), xy_full[:, 0].max(), xy_full[:, 1].max()
        
        dx, dy = (x_max - x_min) * self.crop_margin, (y_max - y_min) * self.crop_margin
        x1, y1 = max(int(x_min - dx), 0), max(int(y_min - dy), 0)
        x2, y2 = min(int(x_max + dx), w0), min(int(y_max + dy), h0)
        
        crop_box = [x1, y1, x2, y2]
        crop = image_bgr[y1:y2, x1:x2]

        if crop.size == 0: return None, image_bgr, None

        crop_resized = cv2.resize(crop, self.target_size, interpolation=cv2.INTER_LINEAR)
        results_crop = self.pose_crop.process(cv2.cvtColor(crop_resized, cv2.COLOR_BGR2RGB))
        annotated_crop = crop_resized.copy()

        if results_crop.pose_landmarks:
            landmarks_crop = [{'x': lm.x, 'y': lm.y, 'z': lm.z, 'visibility': lm.visibility} for lm in results_crop.pose_landmarks.landmark]
            self.mp_drawing.draw_landmarks(annotated_crop, results_crop.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        else:
            landmarks_crop = None
        
        return landmarks_crop, annotated_crop, crop_box

    def close(self):
        self.pose_full.close()
        self.pose_crop.close()