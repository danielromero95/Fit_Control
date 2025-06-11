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
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from frame_extraction import extract_and_preprocess_frames # ¡La importación clave!

_project_root = None

def find_project_root():
    """
    Encuentra la ruta raíz del proyecto de forma robusta.
    """
    global _project_root
    if _project_root:
        return _project_root
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        path = os.path.abspath(__file__)
        while os.path.basename(path) != 'gym-performance-analysis':
            parent_path = os.path.dirname(path)
            if parent_path == path:
                base_path = os.getcwd()
                print(f"ADVERTENCIA: Raíz 'gym-performance-analysis' no encontrada. Usando CWD: {base_path}")
                break
            path = parent_path
        else:
            base_path = path
    _project_root = base_path
    return _project_root

# --- Configuración Centralizada de Rutas y Logging ---
PROJECT_ROOT = find_project_root()
THEMES_DIR   = os.path.join(PROJECT_ROOT, 'themes')
LOG_DIR      = os.path.join(PROJECT_ROOT, 'logs')

os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'app.log'), encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Project root set to: {PROJECT_ROOT}")

def load_stylesheet(app, dark=False):
    """Carga una hoja de estilos QSS para la aplicación."""
    qss_file = 'dark.qss' if dark else 'light.qss'
    path = os.path.join(THEMES_DIR, qss_file)
    if not os.path.exists(path):
        logger.warning(f"Stylesheet not found at {path}")
        return
    try:
        with open(path, 'r') as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        logger.warning(f"Could not load stylesheet {qss_file}: {e}")

# --- WorkerThread ---
class WorkerThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, settings):
        super().__init__()
        self.settings = settings

    def run(self):
        try:
            # Añadimos el callback al diccionario de ajustes
            self.settings['progress_callback'] = self.progress_signal.emit
            metadata = extract_and_preprocess_frames(**self.settings)
            
            self.finished_signal.emit(metadata)
        except Exception as e:
            logger.exception("Error en WorkerThread")
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
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(self.normal_style)

    def dropEvent(self, event):
        self.setStyleSheet(self.normal_style)
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                self.file_dropped.emit(path)
                break

    def show_thumbnail(self, pixmap: QPixmap):
        self.label.setStyleSheet("background: transparent;")
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gym Performance Analyzer")
        self.resize(700, 600)
        self.video_path = None
        self._init_ui()

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
        
        self.process_btn = QPushButton("Procesar vídeo")
        self.process_btn.setEnabled(False)
        self.process_btn.clicked.connect(self._start)
        layout.addWidget(self.process_btn)
        
        return widget

    def _settings_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        default_output = os.path.join(PROJECT_ROOT, 'data', 'processed', 'frames')
        
        self.out_edit = QLineEdit(default_output)
        dir_btn = QPushButton("...")
        dir_btn.clicked.connect(self._open_dir)
        h = QHBoxLayout(); h.addWidget(self.out_edit); h.addWidget(dir_btn)
        layout.addRow("Carpeta salida:", h)
        
        self.sample = QSpinBox(); self.sample.setMinimum(1); self.sample.setValue(3)
        layout.addRow("Sample Rate:", self.sample)
        
        self.rotate = QComboBox(); self.rotate.addItems(["0","90","180","270"]); self.rotate.setCurrentText("90")
        layout.addRow("Rotación (°):", self.rotate)
        
        self.wi = QSpinBox(); self.wi.setRange(16,4096); self.wi.setValue(256)
        self.he = QSpinBox(); self.he.setRange(16,4096); self.he.setValue(256)
        layout.addRow("Ancho (px):", self.wi)
        layout.addRow("Alto (px):", self.he)
        
        self.norm = QCheckBox("Normalizar")
        self.norm.setChecked(True)
        layout.addRow(self.norm)
        
        self.dark_mode = QCheckBox("Modo oscuro")
        self.dark_mode.stateChanged.connect(self._toggle_theme)
        layout.addRow(self.dark_mode)
        
        return widget

    def _toggle_theme(self, state):
        load_stylesheet(QApplication.instance(), dark=(state == Qt.Checked))

    def _video_selected(self, path):
        self.video_path = path
        cap = cv2.VideoCapture(path)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, _ = frame_rgb.shape
            dw, dh = self.drag_widget.width(), self.drag_widget.height()
            
            if w > 0 and h > 0 and dw > 0 and dh > 0:
                scale = min(dw / w, dh / h)
                thumb = cv2.resize(frame_rgb, (int(w * scale), int(h * scale)))
                img = QImage(thumb.data, thumb.shape[1], thumb.shape[0], thumb.strides[0], QImage.Format_RGB888)
                self.drag_widget.show_thumbnail(QPixmap.fromImage(img))

        self.process_btn.setEnabled(True)
        self.progress.setValue(0)

    def _open_file(self):
        default_input = os.path.join(PROJECT_ROOT, 'data', 'raw')
        file, _ = QFileDialog.getOpenFileName(self, "Seleccionar vídeo", default_input, "Vídeos (*.mp4 *.mov *.avi *.mkv)")
        if file:
            self._video_selected(file)
    
    def _open_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta", self.out_edit.text())
        if d:
            self.out_edit.setText(d)

    def _start(self):
        if not self.video_path:
            QMessageBox.critical(self, "Error", "No se ha seleccionado ningún vídeo.")
            return

        base_output_dir = self.out_edit.text().strip()
        video_name = os.path.splitext(os.path.basename(self.video_path))[0]
        final_output_dir = os.path.join(base_output_dir, video_name)
        
        settings = {
            'video_path': self.video_path, 'output_dir': final_output_dir,
            'sample_rate': self.sample.value(), 'rotate': int(self.rotate.currentText()),
            'target_width': self.wi.value(), 'target_height': self.he.value(),
            'normalize': self.norm.isChecked()
        }
        
        self.worker = WorkerThread(settings)
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.error_signal.connect(self._on_processing_error)
        self.worker.finished_signal.connect(self._on_processing_finished)
        self.worker.finished.connect(lambda: self._set_processing_state(False))
        
        self._set_processing_state(True)
        self.worker.start()
        
    def _set_processing_state(self, is_processing):
        """Activa o desactiva la UI para evitar interacciones durante el proceso."""
        is_enabled = not is_processing
        self.tabs.setTabEnabled(1, is_enabled) # Pestaña de Ajustes
        self.select_video_btn.setEnabled(is_enabled)
        self.process_btn.setEnabled(is_enabled and self.video_path is not None)
        
    def _on_processing_error(self, error_message):
        QMessageBox.critical(self, "Error de Procesamiento", error_message)

    def _on_processing_finished(self, metadata):
        output_dir = self.worker.settings['output_dir']
        msg = (f"¡Proceso finalizado!\n\n"
               f"Fotogramas guardados: {metadata['frames_saved']}\n"
               f"Directorio: {output_dir}")
        QMessageBox.information(self, "Finalizado", msg)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    load_stylesheet(app, dark=False)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())