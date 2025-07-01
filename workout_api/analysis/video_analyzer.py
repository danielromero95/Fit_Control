"""
Analizador de Video mejorado para Fit_Control - Compatible con Python 3.13

Este módulo proporciona análisis de ejercicios usando OpenCV y técnicas de 
computer vision sin depender de MediaPipe.

Características:
- Detección de poses usando métodos alternativos
- Análisis de movimiento con filtros de Kalman
- Conteo de repeticiones robusto
- Evaluación de técnica sin MediaPipe
"""

import cv2
import numpy as np
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from scipy.signal import find_peaks
from filterpy.kalman import KalmanFilter
from scipy.spatial.distance import euclidean
import math

logger = logging.getLogger(__name__)


@dataclass
class PoseKeypoint:
    """Punto clave de pose detectado."""
    x: float
    y: float
    confidence: float


@dataclass
class PoseFrame:
    """Frame de análisis de pose."""
    keypoints: Dict[str, PoseKeypoint]
    timestamp: float
    frame_number: int


@dataclass
class AnalysisResult:
    """Resultado del análisis de video."""
    rep_count: int
    form_score: float
    feedback: List[str]
    joint_angles: Dict[str, List[float]]
    movement_quality: Dict[str, float]
    recommendations: List[str]
    processing_time: float
    frame_count: int


class PoseDetectorCV:
    """
    Detector de poses usando OpenCV sin MediaPipe.
    Implementa técnicas alternativas para detección de poses.
    """
    
    def __init__(self):
        """Inicializa el detector de poses."""
        # Detectores de características
        self.body_cascade = None
        self.setup_detectors()
        
        # Filtros de Kalman para suavizar tracking
        self.kalman_filters = {}
        self.prev_keypoints = None
        
    def setup_detectors(self):
        """Configura los detectores de OpenCV."""
        try:
            # Intentar cargar detectores pre-entrenados de OpenCV
            cascade_path = cv2.data.haarcascades + 'haarcascade_fullbody.xml'
            self.body_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.body_cascade.empty():
                logger.warning("No se pudo cargar detector de cuerpo completo")
                
        except Exception as e:
            logger.error(f"Error configurando detectores: {e}")
    
    def detect_pose(self, frame: np.ndarray) -> Optional[Dict[str, PoseKeypoint]]:
        """
        Detecta pose en un frame usando técnicas de OpenCV.
        
        Args:
            frame: Frame de video a analizar
            
        Returns:
            Diccionario con keypoints detectados o None si no se detecta pose
        """
        try:
            height, width = frame.shape[:2]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detectar contornos y formas corporales
            keypoints = self._detect_body_keypoints(frame, gray)
            
            # Aplicar filtros de Kalman para suavizar
            if keypoints:
                keypoints = self._apply_kalman_smoothing(keypoints)
                
            return keypoints
            
        except Exception as e:
            logger.error(f"Error en detección de pose: {e}")
            return None
    
    def _detect_body_keypoints(self, frame: np.ndarray, gray: np.ndarray) -> Dict[str, PoseKeypoint]:
        """
        Detecta keypoints corporales usando análisis de contornos y características.
        
        Esta es una implementación simplificada que puede mejorarse con modelos
        más avanzados cuando MediaPipe esté disponible.
        """
        keypoints = {}
        height, width = frame.shape[:2]
        
        # Detectar cuerpo completo si está disponible el clasificador
        if self.body_cascade and not self.body_cascade.empty():
            bodies = self.body_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(bodies) > 0:
                # Tomar el cuerpo más grande detectado
                x, y, w, h = max(bodies, key=lambda b: b[2] * b[3])
                
                # Estimar keypoints basándose en proporciones corporales típicas
                keypoints = self._estimate_keypoints_from_body_box(x, y, w, h)
        
        # Si no hay detección de cuerpo, usar detección de contornos
        if not keypoints:
            keypoints = self._detect_keypoints_from_contours(frame, gray)
        
        return keypoints
    
    def _estimate_keypoints_from_body_box(self, x: int, y: int, w: int, h: int) -> Dict[str, PoseKeypoint]:
        """Estima keypoints basándose en un bounding box del cuerpo."""
        keypoints = {}
        
        # Proporciones típicas del cuerpo humano
        proportions = {
            'nose': (0.5, 0.1),
            'left_shoulder': (0.25, 0.25),
            'right_shoulder': (0.75, 0.25),
            'left_elbow': (0.15, 0.45),
            'right_elbow': (0.85, 0.45),
            'left_wrist': (0.1, 0.65),
            'right_wrist': (0.9, 0.65),
            'left_hip': (0.35, 0.6),
            'right_hip': (0.65, 0.6),
            'left_knee': (0.3, 0.8),
            'right_knee': (0.7, 0.8),
            'left_ankle': (0.25, 0.95),
            'right_ankle': (0.75, 0.95),
        }
        
        for joint, (rel_x, rel_y) in proportions.items():
            kp_x = x + rel_x * w
            kp_y = y + rel_y * h
            keypoints[joint] = PoseKeypoint(kp_x, kp_y, 0.7)  # Confianza moderada
        
        return keypoints
    
    def _detect_keypoints_from_contours(self, frame: np.ndarray, gray: np.ndarray) -> Dict[str, PoseKeypoint]:
        """Detecta keypoints usando análisis de contornos."""
        keypoints = {}
        
        # Aplicar filtros para mejorar detección
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Encontrar el contorno más grande (probablemente el cuerpo)
            largest_contour = max(contours, key=cv2.contourArea)
            
            if cv2.contourArea(largest_contour) > 1000:  # Filtrar contornos muy pequeños
                # Encontrar puntos extremos del contorno
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                # Estimar keypoints básicos
                keypoints = self._estimate_keypoints_from_body_box(x, y, w, h)
        
        return keypoints
    
    def _apply_kalman_smoothing(self, keypoints: Dict[str, PoseKeypoint]) -> Dict[str, PoseKeypoint]:
        """Aplica filtros de Kalman para suavizar el tracking."""
        smoothed_keypoints = {}
        
        for joint_name, keypoint in keypoints.items():
            if joint_name not in self.kalman_filters:
                # Inicializar filtro de Kalman para esta articulación
                kf = KalmanFilter(dim_x=4, dim_z=2)
                kf.F = np.array([[1, 0, 1, 0],
                               [0, 1, 0, 1],
                               [0, 0, 1, 0],
                               [0, 0, 0, 1]])
                kf.H = np.array([[1, 0, 0, 0],
                               [0, 1, 0, 0]])
                kf.R *= 0.05
                kf.Q *= 0.02
                kf.x = np.array([keypoint.x, keypoint.y, 0, 0])
                self.kalman_filters[joint_name] = kf
            
            # Actualizar filtro
            kf = self.kalman_filters[joint_name]
            kf.predict()
            kf.update([keypoint.x, keypoint.y])
            
            # Crear keypoint suavizado
            smoothed_keypoints[joint_name] = PoseKeypoint(
                x=float(kf.x[0]),
                y=float(kf.x[1]),
                confidence=keypoint.confidence
            )
        
        return smoothed_keypoints


class ExerciseAnalyzerCV:
    """
    Analizador de ejercicios mejorado usando OpenCV.
    Compatible con Python 3.13 sin dependencia de MediaPipe.
    """
    
    def __init__(self):
        """Inicializa el analizador."""
        self.pose_detector = PoseDetectorCV()
        self.pose_history = []
        self.rep_counter = RepetitionCounterCV()
        self.form_analyzer = FormAnalyzerCV()
        
    def analyze_video(self, video_path: str, exercise_type: str = "general") -> AnalysisResult:
        """
        Analiza un video de ejercicio completo.
        
        Args:
            video_path: Ruta al archivo de video
            exercise_type: Tipo de ejercicio a analizar
            
        Returns:
            Resultado completo del análisis
        """
        import time
        start_time = time.time()
        
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"No se pudo abrir el video: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS) or 30
            frame_count = 0
            self.pose_history = []
            
            logger.info(f"Analizando video: {video_path} (ejercicio: {exercise_type})")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Detectar pose en el frame actual
                keypoints = self.pose_detector.detect_pose(frame)
                
                if keypoints:
                    timestamp = frame_count / fps
                    pose_frame = PoseFrame(
                        keypoints=keypoints,
                        timestamp=timestamp,
                        frame_number=frame_count
                    )
                    self.pose_history.append(pose_frame)
                
                frame_count += 1
                
                # Log progreso cada 100 frames
                if frame_count % 100 == 0:
                    logger.debug(f"Procesados {frame_count} frames")
            
            cap.release()
            
            # Realizar análisis completo
            result = self._perform_analysis(exercise_type)
            result.frame_count = frame_count
            result.processing_time = time.time() - start_time
            
            logger.info(f"Análisis completado: {result.rep_count} repeticiones, "
                       f"puntuación: {result.form_score:.1f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error analizando video: {e}")
            return AnalysisResult(
                rep_count=0,
                form_score=0.0,
                feedback=["Error en el análisis"],
                joint_angles={},
                movement_quality={},
                recommendations=[],
                processing_time=time.time() - start_time,
                frame_count=0
            )
    
    def _perform_analysis(self, exercise_type: str) -> AnalysisResult:
        """Realiza el análisis completo de los datos de pose."""
        if not self.pose_history:
            return AnalysisResult(
                rep_count=0,
                form_score=0.0,
                feedback=["No se detectaron poses en el video"],
                joint_angles={},
                movement_quality={},
                recommendations=["Asegúrate de estar bien visible en el video"],
                processing_time=0.0,
                frame_count=0
            )
        
        # Contar repeticiones
        rep_count = self.rep_counter.count_repetitions(self.pose_history, exercise_type)
        
        # Analizar forma
        form_analysis = self.form_analyzer.analyze_form(self.pose_history, exercise_type)
        
        # Calcular ángulos de articulaciones
        joint_angles = self._calculate_joint_angles()
        
        # Evaluar calidad del movimiento
        movement_quality = self._assess_movement_quality()
        
        return AnalysisResult(
            rep_count=rep_count,
            form_score=form_analysis['score'],
            feedback=form_analysis['feedback'],
            joint_angles=joint_angles,
            movement_quality=movement_quality,
            recommendations=form_analysis['recommendations'],
            processing_time=0.0,
            frame_count=len(self.pose_history)
        )
    
    def _calculate_joint_angles(self) -> Dict[str, List[float]]:
        """Calcula ángulos de articulaciones a lo largo del tiempo."""
        joint_angles = {}
        
        angle_configs = {
            'left_elbow': ['left_shoulder', 'left_elbow', 'left_wrist'],
            'right_elbow': ['right_shoulder', 'right_elbow', 'right_wrist'],
            'left_knee': ['left_hip', 'left_knee', 'left_ankle'],
            'right_knee': ['right_hip', 'right_knee', 'right_ankle'],
        }
        
        for joint_name, (p1, p2, p3) in angle_configs.items():
            angles = []
            
            for pose_frame in self.pose_history:
                try:
                    if all(point in pose_frame.keypoints for point in [p1, p2, p3]):
                        kp1 = pose_frame.keypoints[p1]
                        kp2 = pose_frame.keypoints[p2]
                        kp3 = pose_frame.keypoints[p3]
                        
                        angle = self._calculate_angle(
                            (kp1.x, kp1.y),
                            (kp2.x, kp2.y),
                            (kp3.x, kp3.y)
                        )
                        angles.append(angle)
                except Exception:
                    continue
            
            if angles:
                joint_angles[joint_name] = angles
        
        return joint_angles
    
    def _calculate_angle(self, p1: Tuple[float, float], p2: Tuple[float, float], 
                        p3: Tuple[float, float]) -> float:
        """Calcula el ángulo entre tres puntos."""
        try:
            # Vectores
            v1 = np.array([p1[0] - p2[0], p1[1] - p2[1]])
            v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]])
            
            # Calcular ángulo
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            angle = np.arccos(cos_angle) * 180 / np.pi
            
            return float(angle)
        except Exception:
            return 0.0
    
    def _assess_movement_quality(self) -> Dict[str, float]:
        """Evalúa la calidad del movimiento."""
        if len(self.pose_history) < 10:
            return {'speed': 0.0, 'consistency': 0.0, 'range_of_motion': 0.0}
        
        # Calcular velocidades de movimiento
        speeds = []
        for i in range(1, len(self.pose_history)):
            prev_pose = self.pose_history[i-1]
            curr_pose = self.pose_history[i]
            
            if 'left_wrist' in prev_pose.keypoints and 'left_wrist' in curr_pose.keypoints:
                prev_wrist = prev_pose.keypoints['left_wrist']
                curr_wrist = curr_pose.keypoints['left_wrist']
                
                distance = euclidean([prev_wrist.x, prev_wrist.y], 
                                   [curr_wrist.x, curr_wrist.y])
                time_diff = curr_pose.timestamp - prev_pose.timestamp
                
                if time_diff > 0:
                    speed = distance / time_diff
                    speeds.append(speed)
        
        # Evaluar consistencia (variabilidad de velocidad)
        speed_consistency = 1.0 - (np.std(speeds) / np.mean(speeds)) if speeds else 0.0
        speed_consistency = max(0.0, min(1.0, speed_consistency))
        
        # Evaluar velocidad promedio (normalizada)
        avg_speed = np.mean(speeds) if speeds else 0.0
        normalized_speed = min(1.0, avg_speed / 100.0)  # Normalizar a 0-1
        
        # Evaluar rango de movimiento (simplificado)
        range_of_motion = self._calculate_range_of_motion()
        
        return {
            'speed': float(normalized_speed),
            'consistency': float(speed_consistency),
            'range_of_motion': float(range_of_motion)
        }
    
    def _calculate_range_of_motion(self) -> float:
        """Calcula el rango de movimiento promedio."""
        if not self.pose_history:
            return 0.0
        
        # Usar muñeca izquierda como referencia
        wrist_positions = []
        for pose_frame in self.pose_history:
            if 'left_wrist' in pose_frame.keypoints:
                wrist = pose_frame.keypoints['left_wrist']
                wrist_positions.append([wrist.x, wrist.y])
        
        if len(wrist_positions) < 2:
            return 0.0
        
        # Calcular rango máximo de movimiento
        wrist_positions = np.array(wrist_positions)
        x_range = np.max(wrist_positions[:, 0]) - np.min(wrist_positions[:, 0])
        y_range = np.max(wrist_positions[:, 1]) - np.min(wrist_positions[:, 1])
        
        # Normalizar rango (asumiendo resolución de video típica)
        total_range = np.sqrt(x_range**2 + y_range**2)
        normalized_range = min(1.0, total_range / 200.0)  # Normalizar a 0-1
        
        return normalized_range


class RepetitionCounterCV:
    """Contador de repeticiones usando análisis de señales."""
    
    def count_repetitions(self, pose_history: List[PoseFrame], exercise_type: str) -> int:
        """Cuenta repeticiones basándose en el historial de poses."""
        if len(pose_history) < 10:
            return 0
        
        # Seleccionar keypoint relevante según el ejercicio
        keypoint = self._get_relevant_keypoint(exercise_type)
        
        # Extraer señal de movimiento
        signal = self._extract_movement_signal(pose_history, keypoint)
        
        if not signal:
            return 0
        
        # Detectar picos en la señal
        peaks = self._detect_peaks(signal)
        
        # Contar repeticiones (cada 2 picos = 1 repetición)
        rep_count = len(peaks) // 2
        
        return max(0, rep_count)
    
    def _get_relevant_keypoint(self, exercise_type: str) -> str:
        """Obtiene el keypoint más relevante para el ejercicio."""
        keypoint_map = {
            'push_up': 'left_wrist',
            'squat': 'left_hip',
            'bicep_curl': 'left_wrist',
            'shoulder_press': 'left_wrist',
            'general': 'left_wrist'
        }
        return keypoint_map.get(exercise_type, 'left_wrist')
    
    def _extract_movement_signal(self, pose_history: List[PoseFrame], keypoint: str) -> List[float]:
        """Extrae señal de movimiento del keypoint especificado."""
        signal = []
        
        for pose_frame in pose_history:
            if keypoint in pose_frame.keypoints:
                kp = pose_frame.keypoints[keypoint]
                # Usar coordenada Y (vertical) para la mayoría de ejercicios
                signal.append(kp.y)
        
        return signal
    
    def _detect_peaks(self, signal: List[float]) -> List[int]:
        """Detecta picos en la señal de movimiento."""
        if len(signal) < 5:
            return []
        
        # Suavizar señal
        signal = np.array(signal)
        kernel = np.ones(5) / 5
        smoothed = np.convolve(signal, kernel, mode='valid')
        
        # Detectar picos
        peaks, _ = find_peaks(smoothed, height=np.mean(smoothed), distance=10)
        
        return peaks.tolist()


class FormAnalyzerCV:
    """Analizador de forma y técnica de ejercicios."""
    
    def analyze_form(self, pose_history: List[PoseFrame], exercise_type: str) -> Dict[str, Any]:
        """Analiza la forma del ejercicio."""
        if not pose_history:
            return {
                'score': 0.0,
                'feedback': ['No hay datos para analizar'],
                'recommendations': ['Asegúrate de estar visible en el video']
            }
        
        # Análisis específico por ejercicio
        if exercise_type == 'push_up':
            return self._analyze_push_up_form(pose_history)
        elif exercise_type == 'squat':
            return self._analyze_squat_form(pose_history)
        else:
            return self._analyze_general_form(pose_history)
    
    def _analyze_push_up_form(self, pose_history: List[PoseFrame]) -> Dict[str, Any]:
        """Analiza la forma en push-ups."""
        score = 0.7  # Puntuación base
        feedback = []
        recommendations = []
        
        # Verificar alineación del cuerpo
        alignment_score = self._check_body_alignment(pose_history)
        score = (score + alignment_score) / 2
        
        if alignment_score < 0.6:
            feedback.append("Mantén el cuerpo en línea recta")
            recommendations.append("Contrae el core y evita arquear la espalda")
        
        # Verificar rango de movimiento
        rom_score = self._check_range_of_motion(pose_history, 'push_up')
        score = (score + rom_score) / 2
        
        if rom_score < 0.6:
            feedback.append("Aumenta el rango de movimiento")
            recommendations.append("Baja más el pecho hacia el suelo")
        
        return {
            'score': min(1.0, max(0.0, score)),
            'feedback': feedback,
            'recommendations': recommendations
        }
    
    def _analyze_squat_form(self, pose_history: List[PoseFrame]) -> Dict[str, Any]:
        """Analiza la forma en squats."""
        score = 0.7  # Puntuación base
        feedback = []
        recommendations = []
        
        # Verificar profundidad del squat
        depth_score = self._check_squat_depth(pose_history)
        score = (score + depth_score) / 2
        
        if depth_score < 0.6:
            feedback.append("Baja más en el squat")
            recommendations.append("Las caderas deben bajar al nivel de las rodillas")
        
        # Verificar alineación de rodillas
        knee_alignment = self._check_knee_alignment(pose_history)
        score = (score + knee_alignment) / 2
        
        if knee_alignment < 0.6:
            feedback.append("Mantén las rodillas alineadas")
            recommendations.append("Evita que las rodillas se junten hacia adentro")
        
        return {
            'score': min(1.0, max(0.0, score)),
            'feedback': feedback,
            'recommendations': recommendations
        }
    
    def _analyze_general_form(self, pose_history: List[PoseFrame]) -> Dict[str, Any]:
        """Análisis general de forma."""
        score = 0.75  # Puntuación base para ejercicios generales
        feedback = ["Análisis general completado"]
        recommendations = ["Mantén una postura estable y controlada"]
        
        return {
            'score': score,
            'feedback': feedback,
            'recommendations': recommendations
        }
    
    def _check_body_alignment(self, pose_history: List[PoseFrame]) -> float:
        """Verifica la alineación del cuerpo."""
        alignments = []
        
        for pose_frame in pose_history:
            keypoints = pose_frame.keypoints
            required_points = ['left_shoulder', 'left_hip', 'left_ankle']
            
            if all(point in keypoints for point in required_points):
                shoulder = keypoints['left_shoulder']
                hip = keypoints['left_hip']
                ankle = keypoints['left_ankle']
                
                # Calcular alineación (qué tan recta está la línea)
                alignment = self._calculate_line_straightness(
                    (shoulder.x, shoulder.y),
                    (hip.x, hip.y),
                    (ankle.x, ankle.y)
                )
                alignments.append(alignment)
        
        return np.mean(alignments) if alignments else 0.5
    
    def _calculate_line_straightness(self, p1: Tuple[float, float], 
                                   p2: Tuple[float, float], p3: Tuple[float, float]) -> float:
        """Calcula qué tan recta es una línea entre tres puntos."""
        try:
            # Calcular distancia de p2 a la línea entre p1 y p3
            x1, y1 = p1
            x2, y2 = p2
            x3, y3 = p3
            
            # Distancia del punto a la línea
            distance = abs((y3 - y1) * x2 - (x3 - x1) * y2 + x3 * y1 - y3 * x1) / \
                      np.sqrt((y3 - y1)**2 + (x3 - x1)**2)
            
            # Normalizar a score 0-1 (menor distancia = mejor alineación)
            return max(0.0, 1.0 - distance / 50.0)
        except Exception:
            return 0.5
    
    def _check_range_of_motion(self, pose_history: List[PoseFrame], exercise_type: str) -> float:
        """Verifica el rango de movimiento."""
        # Simplificado: usar variación en posición Y de muñeca
        y_positions = []
        
        for pose_frame in pose_history:
            if 'left_wrist' in pose_frame.keypoints:
                y_positions.append(pose_frame.keypoints['left_wrist'].y)
        
        if len(y_positions) < 2:
            return 0.5
        
        # Calcular rango de movimiento
        y_range = max(y_positions) - min(y_positions)
        
        # Normalizar (asumiendo que 100 píxeles es un buen rango)
        normalized_range = min(1.0, y_range / 100.0)
        
        return normalized_range
    
    def _check_squat_depth(self, pose_history: List[PoseFrame]) -> float:
        """Verifica la profundidad del squat."""
        depths = []
        
        for pose_frame in pose_history:
            keypoints = pose_frame.keypoints
            if 'left_hip' in keypoints and 'left_knee' in keypoints:
                hip_y = keypoints['left_hip'].y
                knee_y = keypoints['left_knee'].y
                
                # Profundidad relativa (cadera vs rodilla)
                depth_ratio = (hip_y - knee_y) / abs(hip_y) if hip_y != 0 else 0
                depths.append(abs(depth_ratio))
        
        if not depths:
            return 0.5
        
        avg_depth = np.mean(depths)
        return min(1.0, avg_depth)
    
    def _check_knee_alignment(self, pose_history: List[PoseFrame]) -> float:
        """Verifica la alineación de las rodillas."""
        alignments = []
        
        for pose_frame in pose_history:
            keypoints = pose_frame.keypoints
            required_points = ['left_hip', 'left_knee', 'left_ankle']
            
            if all(point in keypoints for point in required_points):
                hip = keypoints['left_hip']
                knee = keypoints['left_knee']
                ankle = keypoints['left_ankle']
                
                # Verificar que la rodilla esté entre cadera y tobillo horizontalmente
                alignment = 1.0 - abs(knee.x - (hip.x + ankle.x) / 2) / 50.0
                alignments.append(max(0.0, alignment))
        
        return np.mean(alignments) if alignments else 0.5


# Función de utilidad para usar desde las vistas
def analyze_exercise_video(video_path: str, exercise_type: str = "general") -> Dict[str, Any]:
    """
    Función principal para analizar videos de ejercicio.
    
    Args:
        video_path: Ruta al archivo de video
        exercise_type: Tipo de ejercicio
        
    Returns:
        Diccionario con resultados del análisis
    """
    try:
        analyzer = ExerciseAnalyzerCV()
        result = analyzer.analyze_video(video_path, exercise_type)
        
        return {
            'success': True,
            'repetitions_count': result.rep_count,
            'form_score': result.form_score,
            'feedback': result.feedback,
            'joint_angles': result.joint_angles,
            'movement_quality': result.movement_quality,
            'recommendations': result.recommendations,
            'processing_time': result.processing_time,
            'frame_count': result.frame_count,
        }
        
    except Exception as e:
        logger.error(f"Error en análisis de video: {e}")
        return {
            'success': False,
            'error': str(e),
            'repetitions_count': 0,
            'form_score': 0.0,
            'feedback': ['Error en el análisis del video'],
            'joint_angles': {},
            'movement_quality': {},
            'recommendations': ['Verifique que el video sea válido'],
            'processing_time': 0.0,
            'frame_count': 0,
        }