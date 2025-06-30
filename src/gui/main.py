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
from src.database import save_training_plan
from src.gui.pages.plans_page import sample_plan

# Instancia global del traductor
_TRANSLATIONS_PATH = os.path.join(os.path.dirname(__file__), '..', 'i18n', 'es.json')
translator = Translator(os.path.abspath(_TRANSLATIONS_PATH))

# 2) Utils propias
from .main_window import MainWindow
from pathlib import Path
import subprocess


def find_project_root() -> str:
    """Return the repository root directory.

    Falls back to searching for ``config.yaml`` if git is unavailable.
    """
    try:
        root = (
            subprocess.check_output([
                "git",
                "rev-parse",
                "--show-toplevel",
            ],
            text=True)
            .strip()
        )
        return root
    except Exception:
        path = Path(__file__).resolve().parent
        while path != path.parent:
            if (path / "config.yaml").exists() and (path / "src").exists():
                return str(path)
            path = path.parent
        return str(Path.cwd())

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


def _plan_dict_to_markdown(plan: dict) -> str:
    """Convierte un plan dict a Markdown simple."""
    lines = []
    for day in plan.get("days", []):
        lines.append(f"### {day.get('day_name', '')}")
        exercises = day.get("exercises", [])
        if not exercises:
            lines.append("Descanso")
        else:
            for ex in exercises:
                lines.append(f"- {ex.get('name')} {ex.get('detail')}")
        lines.append("")
    return "\n".join(lines)


def _ensure_active_plan() -> None:
    """Guarda el plan de ejemplo como activo si no existe otro."""
    if database.get_active_plan_id() is not None:
        return

    md = _plan_dict_to_markdown(sample_plan)
    plan_id = save_training_plan(sample_plan["plan_name"], md)
    database.set_app_state("active_plan_id", str(plan_id))

def run_app():
    # Determina la raíz del proyecto buscando la carpeta gym-performance-analysis
    PROJECT_ROOT = find_project_root()
    sys.path.insert(0, PROJECT_ROOT)

    setup_logging(PROJECT_ROOT)
    logging.info("Arrancando Gym Performance Analyzer")

    database.init_db()
    _ensure_active_plan()

    app = QApplication(sys.argv)
    # No forzamos aquí el tema: _apply_theme del MainWindow leerá el checkbox
    window = MainWindow(project_root=PROJECT_ROOT, translator=translator)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_app()
