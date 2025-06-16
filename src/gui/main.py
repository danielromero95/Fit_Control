# src/gui/main.py

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings

# --- Importamos desde la nueva utilidad ---
from .style_utils import load_stylesheet

def find_project_root():
    path = os.path.abspath(os.path.dirname(__file__))
    while os.path.basename(path) != 'gym-performance-analysis':
        parent_path = os.path.dirname(path)
        if parent_path == path: return os.getcwd()
        path = parent_path
    return path

def setup_logging(project_root):
    log_dir = os.path.join(project_root, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.FileHandler(os.path.join(log_dir, 'app.log'), encoding='utf-8'), logging.StreamHandler(sys.stdout)])

def run_app():
    """Función para encapsular la creación y ejecución de la app."""
    # Añadimos el path del proyecto para que los imports desde 'src' funcionen bien
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, PROJECT_ROOT)
    
    # Importamos MainWindow aquí dentro para asegurar que el path está configurado
    from src.gui.main_window import MainWindow
    from src.gui.style_utils import load_stylesheet

    app = QApplication(sys.argv)
    
    # La carga del stylesheet ahora puede usar la ruta del proyecto
    load_stylesheet(app, PROJECT_ROOT, dark=True) 

    window = MainWindow(project_root=PROJECT_ROOT)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    # Esta es la única parte que se ejecuta cuando lanzas el script directamente
    run_app()