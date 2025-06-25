# src/gui/style_utils.py

import os
from PyQt5.QtWidgets import QApplication

import logging
logger = logging.getLogger(__name__)

def load_stylesheet(app: QApplication, project_root: str, dark: bool):
    """Carga la hoja de estilos (clara u oscura) para la aplicación."""
    themes_dir = os.path.join(project_root, 'themes')
    qss_file = 'dark.qss' if dark else 'light.qss'
    path = os.path.join(themes_dir, qss_file)
    
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    else:
        logger.warning(f"No se encontró la hoja de estilos en {path}")
