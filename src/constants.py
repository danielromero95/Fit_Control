# src/constants.py

from enum import Enum

"""
Módulo para almacenar constantes fijas de la aplicación.
"""

# Información de la Aplicación
APP_NAME = "Gym Performance Analyzer"
ORGANIZATION_NAME = "TFM-DanielRomero"

# Extensiones de vídeo soportadas
VIDEO_EXTENSIONS = [".mp4", ".mov", ".avi", ".mkv"]

# Valores por defecto para los ajustes de la GUI
DEFAULT_SAMPLE_RATE = 1
DEFAULT_TARGET_WIDTH = 480
DEFAULT_TARGET_HEIGHT = 854
DEFAULT_USE_CROP = True
DEFAULT_GENERATE_VIDEO = True
DEFAULT_DEBUG_MODE = False
DEFAULT_DARK_MODE = True
DEFAULT_ROTATE = 90

class MetricType(str, Enum):
    """Define los tipos de métricas que nuestro analizador puede calcular."""
    ANGLE = "angle"
    HEIGHT = "height"

# Conexiones del modelo de pose de MediaPipe
try:
    from mediapipe.python.solutions.pose import POSE_CONNECTIONS as MP_POSE_CONNECTIONS
    POSE_CONNECTIONS = MP_POSE_CONNECTIONS
except Exception:  # pragma: no cover - MediaPipe not available
    POSE_CONNECTIONS = []

# Colores por defecto para dibujar el esqueleto
CONNECTION_COLOR = (0, 255, 0)  # BGR
LANDMARK_COLOR = (0, 0, 255)    # BGR
