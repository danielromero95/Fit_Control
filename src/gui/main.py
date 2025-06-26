# src/gui/main.py

import os
# ===========================
#  Silenciar logs “verborrea” de C++ / glog / absl / TF
# ===========================
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel']   = '2'
os.environ['GLOG_logtostderr']   = '1'

# silenciar logs de TFLite y MediaPipe
os.environ['TFLITE_CPP_MIN_LOG_LEVEL'] = '3'

import sys
import logging
from PyQt5.QtWidgets import QApplication
from src.i18n.translator import Translator

from src import database

# Instancia global del traductor
_TRANSLATIONS_PATH = os.path.join(os.path.dirname(__file__), '..', 'i18n', 'es.json')
translator = Translator(os.path.abspath(_TRANSLATIONS_PATH))

# 2) Utils propias
from .main_window import MainWindow

def find_project_root():
    path = os.path.abspath(os.path.dirname(__file__))
    while os.path.basename(path) != 'gym-performance-analysis':
        parent = os.path.dirname(path)
        if parent == path:
            return os.getcwd()
        path = parent
    return path

def setup_logging(project_root: str):
    log_dir = os.path.join(project_root, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    fmt = '%(asctime)s [%(levelname)s] %(message)s'
    handlers = [
        logging.FileHandler(os.path.join(log_dir, 'app.log'), encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
    logging.basicConfig(level=logging.INFO, format=fmt, handlers=handlers)

    # 3) Silenciar loggers Python de TF / MP
    logging.getLogger('tensorflow').setLevel(logging.ERROR)
    logging.getLogger('tflite_runtime').setLevel(logging.ERROR)
    logging.getLogger('mediapipe').setLevel(logging.ERROR)

def run_app():
    # Determina la raíz del proyecto buscando la carpeta gym-performance-analysis
    PROJECT_ROOT = find_project_root()
    sys.path.insert(0, PROJECT_ROOT)

    setup_logging(PROJECT_ROOT)
    logging.info("Arrancando Gym Performance Analyzer")

    database.init_db()

    app = QApplication(sys.argv)
    # No forzamos aquí el tema: _apply_theme del MainWindow leerá el checkbox
    window = MainWindow(project_root=PROJECT_ROOT)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_app()
