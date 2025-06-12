# frame_extraction_gui.py

import sys
import os
import cv2
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QFileDialog, QSpinBox, QComboBox, QCheckBox, QVBoxLayout,
    QTabWidget, QMessageBox, QProgressBar, QFormLayout, QHBoxLayout,
    QLineEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt5.QtGui import QPixmap, QImage, QFont

from src.pipeline import run_full_pipeline_in_memory

_project_root = None
def find_project_root():
    global _project_root
    if _project_root: return _project_root
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        path = os.path.abspath(__file__)
        while os.path.basename(path) != 'gym-performance-analysis':
            parent_path = os.path.dirname(path)
            if parent_path == path:
                base_path = os.getcwd()
                break
            path = parent_path
        else:
            base_path = path
    _project_root = base_path
    return _project_root

PROJECT_ROOT = find_project_root()
THEMES_DIR = os.path.join(PROJECT_ROOT, 'themes')
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.FileHandler(os.path.join(LOG_DIR, 'app.log'), encoding='utf-8'), logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

def load_stylesheet(app, dark=False):
    qss_file = 'dark.qss' if dark else 'light.qss'
    path = os.path.join(THEMES_DIR, qss_file)
    if os.path.exists(path):
        with open(path, 'r') as f:
            app.setStyleSheet(f.read())

class WorkerThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, video_path, settings):
        super().__init__()
        self.video_path = video_path
        self.settings = settings

    def run(self):
        try:
            results = run_full_pipeline_in_memory(
                video_path=self.video_path,
                settings=self.settings,
                progress_callback=self.progress_signal.emit
            )
            self.finished_signal.emit(results)
        except Exception as e:
            logger.exception("Error durante la ejecución del pipeline en el WorkerThread")
            self.error_signal.emit(str(e))

class DragDropWidget(QWidget):
    file_dropped = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.default_text = "Arrastra o selecciona tu vídeo aquí"
        self.label = QLabel(self.default_text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: #777; font-size: 16px; background: transparent;")
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self.normal_style = "QWidget { border: 2px dashed #aaa; border-radius: 8px; }"
        self.dragover_style = "QWidget { border: 2px dashed #0078d7; border-radius: 8px; background-color: #e8f0fe; }"
        self.setStyleSheet(self.normal_style)
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self.setStyleSheet(self.dragover_style)
            event.acceptProposedAction()
    def dragLeaveEvent(self, event):
        self.setStyleSheet(self.normal_style)
    def dropEvent(self, event):
        self.setStyleSheet(self.normal_style)
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path): self.file_dropped.emit(path)
            break
    def show_thumbnail(self, pixmap: QPixmap):
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gym Performance Analyzer")
        self.resize(700, 650)
        self.video_path = None
        self.settings = QSettings("GymPerformance", "AnalyzerApp")
        self._init_ui()
        self._load_settings()

    def _init_ui(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(self._home_tab(), "Inicio")
        self.tabs.addTab(self._settings_tab(), "Ajustes")
        self.setCentralWidget(self.tabs)

    def _home_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.drag_widget = DragDropWidget()
        self.drag_widget.file_dropped.connect(self._video_selected)
        layout.addWidget(self.drag_widget)
        self.select_video_btn = QPushButton("Seleccionar vídeo")
        self.select_video_btn.clicked.connect(self._open_file)
        layout.addWidget(self.select_video_btn)
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        self.results_label = QLabel("Los resultados del análisis aparecerán aquí.")
        self.results_label.setAlignment(Qt.AlignCenter)
        font = QFont(); font.setPointSize(14); font.setBold(True)
        self.results_label.setFont(font)
        self.results_label.setStyleSheet("color: #333; padding: 10px; border-radius: 5px; background-color: #f0f0f0;")
        layout.addWidget(self.results_label)
        self.process_btn = QPushButton("Analizar Vídeo")
        self.process_btn.setEnabled(False)
        self.process_btn.clicked.connect(self._start)
        layout.addWidget(self.process_btn)
        return widget

    def _settings_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        self.out_edit = QLineEdit()
        self.sample = QSpinBox(); self.sample.setMinimum(1)
        self.rotate = QComboBox(); self.rotate.addItems(["0","90","180","270"])
        self.wi = QSpinBox(); self.wi.setRange(16,4096)
        self.he = QSpinBox(); self.he.setRange(16,4096)
        self.use_crop_check = QCheckBox("Usar recorte centrado (más preciso)")
        self.use_crop_check.setToolTip("Realiza una detección en dos pasadas para centrarse en la persona. Más lento pero más preciso.")
        
        # --- Checkbox para generar el vídeo ---
        self.generate_video_check = QCheckBox("Generar vídeo de depuración con esqueleto")
        self.generate_video_check.setToolTip("Crea un archivo .mp4 con el esqueleto dibujado para verificar la detección.")

        self.dark_mode = QCheckBox("Modo oscuro")
        self.dark_mode.stateChanged.connect(self._toggle_theme)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.wi)
        h_layout.addWidget(QLabel("x"))
        h_layout.addWidget(self.he)
        layout.addRow("Carpeta base de salida:", self.out_edit)
        layout.addRow("Sample Rate (1 de cada N frames):", self.sample)
        layout.addRow("Rotación (°):", self.rotate)
        layout.addRow("Ancho/Alto (px) de preproceso:", h_layout)
        layout.addRow(self.use_crop_check)
        layout.addRow(self.generate_video_check)
        layout.addRow(self.dark_mode)
        return widget

    def _toggle_theme(self, state):
        is_dark = (state == Qt.Checked)
        load_stylesheet(QApplication.instance(), dark=is_dark)

    def _video_selected(self, path):
        self.video_path = path
        self.results_label.setText("Vídeo cargado. Listo para analizar.")
        self.results_label.setStyleSheet("color: #0057e7; padding: 10px; border-radius: 5px; background-color: #e8f0fe;")
        cap = cv2.VideoCapture(path)
        ret, frame = cap.read()
        cap.release()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pixmap = QPixmap.fromImage(QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], frame_rgb.strides[0], QImage.Format_RGB888))
            self.drag_widget.show_thumbnail(pixmap.scaled(self.drag_widget.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.process_btn.setEnabled(True)
        self.progress.setValue(0)

    def _start(self):
        if not self.video_path:
            QMessageBox.critical(self, "Error", "No se ha seleccionado ningún vídeo.")
            return
        settings = {
            'output_dir': self.out_edit.text().strip(),
            'sample_rate': self.sample.value(),
            'rotate': int(self.rotate.currentText()),
            'target_width': self.wi.value(),
            'target_height': self.he.value(),
            'use_crop': self.use_crop_check.isChecked(),
            'generate_debug_video': self.generate_video_check.isChecked()
        }
        self.worker = WorkerThread(self.video_path, settings)
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.error_signal.connect(self._on_processing_error)
        self.worker.finished_signal.connect(self._on_processing_finished)
        self.worker.finished.connect(lambda: self._set_processing_state(False))
        self._set_processing_state(True)
        self.worker.start()

    def _set_processing_state(self, is_processing):
        is_enabled = not is_processing
        self.tabs.setTabEnabled(1, is_enabled)
        self.select_video_btn.setEnabled(is_enabled)
        self.process_btn.setEnabled(is_enabled and self.video_path is not None)
        if is_processing:
            self.results_label.setText("Procesando... por favor, espere.")
            self.results_label.setStyleSheet("color: #f39c12; padding: 10px; border-radius: 5px; background-color: #fef9e7;")

    def _on_processing_error(self, error_message):
        self.results_label.setText(f"Error: {error_message}")
        self.results_label.setStyleSheet("color: #c0392b; padding: 10px; border-radius: 5px; background-color: #fdedec;")
        QMessageBox.critical(self, "Error de Procesamiento", error_message)

    def _on_processing_finished(self, results):
        rep_count = results.get("repeticiones_contadas", "N/A")
        self.results_label.setText(f"¡Análisis Completo! Repeticiones detectadas: {rep_count}")
        self.results_label.setStyleSheet("color: #27ae60; padding: 10px; border-radius: 5px; background-color: #eafaf1;")
        QMessageBox.information(self, "Finalizado", f"Análisis completado.\n\nRepeticiones contadas: {rep_count}")

    def _load_settings(self):
        self.out_edit.setText(self.settings.value("output_dir", os.path.join(PROJECT_ROOT, 'data', 'processed')))
        self.sample.setValue(self.settings.value("sample_rate", 1, type=int))
        self.rotate.setCurrentText(self.settings.value("rotation", "90"))
        self.wi.setValue(self.settings.value("width", 256, type=int))
        self.he.setValue(self.settings.value("height", 256, type=int))
        self.use_crop_check.setChecked(self.settings.value("use_crop", True, type=bool))
        self.generate_video_check.setChecked(self.settings.value("generate_debug_video", False, type=bool))
        is_dark = self.settings.value("dark_mode", False, type=bool)
        self.dark_mode.setChecked(is_dark)
        self._toggle_theme(Qt.Checked if is_dark else Qt.Unchecked)

    def closeEvent(self, event):
        self.settings.setValue("output_dir", self.out_edit.text())
        self.settings.setValue("sample_rate", self.sample.value())
        self.settings.setValue("rotation", self.rotate.currentText())
        self.settings.setValue("width", self.wi.value())
        self.settings.setValue("height", self.he.value())
        self.settings.setValue("use_crop", self.use_crop_check.isChecked())
        self.settings.setValue("generate_debug_video", self.generate_video_check.isChecked())
        self.settings.setValue("dark_mode", self.dark_mode.isChecked())
        super().closeEvent(event)

    def _open_file(self):
        default_input = os.path.dirname(self.video_path) if self.video_path else os.path.join(PROJECT_ROOT, 'data', 'raw')
        file, _ = QFileDialog.getOpenFileName(self, "Seleccionar vídeo", default_input, "Vídeos (*.mp4 *.mov *.avi *.mkv)")
        if file: self._video_selected(file)

    def _open_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta", self.out_edit.text())
        if d: self.out_edit.setText(d)

    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())