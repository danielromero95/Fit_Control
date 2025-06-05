import os
import pytest
import tempfile
import cv2

from src.A_preprocessing.video_utils import validate_video

def create_dummy_video(path, width=64, height=48, num_frames=30, fps=15):
    """
    Crea un vídeo muy sencillo en path con OpenCV (imagen en negro)
    para usar en los tests.
    """
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(path, fourcc, fps, (width, height))
    if not writer.isOpened():
        writer.release()
        raise RuntimeError("No se pudo abrir VideoWriter para crear vídeo de prueba")
    # Generar frames negros
    frame = (0 * np.ones((height, width, 3))).astype('uint8')
    for _ in range(num_frames):
        writer.write(frame)
    writer.release()

def test_validate_video_ok(tmp_path):
    # 1. Crear un vídeo de prueba
    dummy_video = tmp_path / "test_ok.mp4"
    create_dummy_video(str(dummy_video), width=64, height=48, num_frames=30, fps=15)

    # 2. Llamar a validate_video y comprobar valores
    info = validate_video(str(dummy_video))
    assert isinstance(info, dict)
    # fps debería ser 15 (o muy cercano)
    assert abs(info["fps"] - 15) < 1e-3
    # frame_count debería ser 30
    assert info["frame_count"] == 30
    # duration ≈ 30/15 = 2.0 segundos
    assert abs(info["duration"] - 2.0) < 1e-3

def test_validate_video_no_exist():
    # Ruta inexistente: debe lanzar IOError
    with pytest.raises(IOError):
        validate_video("ruta/que/no/existe/video.avi")

def test_validate_video_corrupt(tmp_path, monkeypatch):
    # Simular que CAP_PROP_FPS devuelve 0 → ValueError
    dummy_video = tmp_path / "corrupt.mp4"
    create_dummy_video(str(dummy_video), width=64, height=48, num_frames=10, fps=10)

    # Forzamos que cap.get(CAP_PROP_FPS) devuelva 0
    class FakeCap:
        def __init__(self, path):
            self.opened = True
        def isOpened(self):
            return True
        def get(self, prop):
            # para FPS devolvemos 0
            if prop == cv2.CAP_PROP_FPS:
                return 0
            elif prop == cv2.CAP_PROP_FRAME_COUNT:
                return 10
            return 0
        def release(self):
            pass

    monkeypatch.setattr(cv2, "VideoCapture", lambda x: FakeCap(x))

    with pytest.raises(ValueError):
        validate_video(str(dummy_video))