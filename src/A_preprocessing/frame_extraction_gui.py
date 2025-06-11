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


_project_root = None

def find_project_root():
    """
    Encuentra la ruta raíz del proyecto de forma robusta.
    - En modo "congelado" (despliegue), usa la ruta del ejecutable.
    - En modo normal (desarrollo), busca hacia arriba la carpeta 'gym-performance-analysis'.
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

# --- Configuración de Rutas y Logging ---

# Usa la función para definir las rutas base
PROJECT_ROOT = find_project_root()
THEMES_DIR   = os.path.join(PROJECT_ROOT, 'themes')
LOG_DIR      = os.path.join(PROJECT_ROOT, 'logs') # Para despliegue, considera una carpeta de datos de usuario

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

# Cargamos el stylesheet por defecto (puede ser 'dark.qss' o 'light.qss')
def load_stylesheet(app, dark=False):
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
        self.dragover_style = "QWidget { border: 2px dashed #5a9; border-radius: 8px; background-color: #efe; }"
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

    def clear(self):
        self.label.clear()
        self.label.setText(self.default_text)
        self.label.setStyleSheet("color: #777; font-size: 16px; background: transparent;")

class WorkerThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, video_path, output_dir, sample_rate, rotate,
                 target_width, target_height, normalize):
        super().__init__()
        self.video_path = video_path
        self.output_dir = output_dir
        self.sample_rate = sample_rate
        self.rotate = rotate
        self.target_width = target_width
        self.target_height = target_height
        self.normalize = normalize

    def run(self):
        try:
            logger.info(f"Processing {self.video_path}")
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                raise IOError(f"Cannot open video: {self.video_path}")
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            os.makedirs(self.output_dir, exist_ok=True)

            saved = 0
            idx = 0
            step = max(frame_count // 100, 1)
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if idx % self.sample_rate == 0:
                    if self.rotate == 90:
                        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                    elif self.rotate == 180:
                        frame = cv2.rotate(frame, cv2.ROTATE_180)
                    elif self.rotate == 270:
                        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    frame = cv2.resize(frame, (self.target_width, self.target_height), interpolation=cv2.INTER_AREA)
                    if self.normalize:
                        frame = (frame.astype('float32') / 255.0 * 255.0).astype('uint8')
                    fname = os.path.join(self.output_dir, f"frame_{saved+1:04d}.jpg")
                    cv2.imwrite(fname, frame)
                    saved += 1
                idx += 1
                if idx % step == 0 and frame_count > 0:
                    self.progress_signal.emit(int(idx / frame_count * 100))

            cap.release()
            self.progress_signal.emit(100)
            metadata = {
                'fps': fps,
                'frame_count': frame_count,
                'duration': frame_count / fps if fps else 0,
                'frames_saved': saved
            }
            logger.info(f"Finished: {saved} frames in {self.output_dir}")
            self.finished_signal.emit(metadata)
        except Exception as e:
            logger.exception("WorkerThread error")
            self.error_signal.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gym Performance Analyzer")
        self.resize(700, 600)
        self.video_path = None
        self.output_folder = None
        self._init_ui()

    def _init_ui(self):
        tabs = QTabWidget()
        tabs.addTab(self._home_tab(), "Inicio")
        tabs.addTab(self._settings_tab(), "Ajustes")
        self.setCentralWidget(tabs)

    def _home_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.drag_widget = DragDropWidget()
        self.drag_widget.file_dropped.connect(self._video_selected)
        layout.addWidget(self.drag_widget)

        btn = QPushButton("Seleccionar vídeo")
        btn.clicked.connect(self._open_file)
        layout.addWidget(btn)

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
        
        # Usa PROJECT_ROOT para una ruta por defecto más inteligente
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
        base_output = self.out_edit.text().strip()
        name = os.path.splitext(os.path.basename(path))[0]
        self.output_folder = os.path.join(base_output, name)
        
        # MEJORA: No llames a clear() para evitar el parpadeo.
        # self.drag_widget.clear() 
        
        cap = cv2.VideoCapture(path)
        ret, frame = cap.read()
        cap.release()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, _ = frame.shape
            dw, dh = self.drag_widget.width(), self.drag_widget.height()
            
            # Evita división por cero si el widget no es visible aún
            if w == 0 or h == 0 or dw == 0 or dh == 0:
                self.process_btn.setEnabled(True)
                return

            scale = min(dw / w, dh / h)
            thumb = cv2.resize(frame, (int(w * scale), int(h * scale)))
            img = QImage(thumb.data, thumb.shape[1], thumb.shape[0], thumb.strides[0], QImage.Format_RGB888)
            pix = QPixmap.fromImage(img)
            self.drag_widget.show_thumbnail(pix)

        self.process_btn.setEnabled(True)
        self.progress.setValue(0)


    def _open_file(self):
        # Usa PROJECT_ROOT para una ruta por defecto más inteligente
        default_input = os.path.join(PROJECT_ROOT, 'data', 'raw')
        file, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar vídeo", default_input, "Vídeos (*.mp4 *.mov *.avi *.mkv)")
        if file:
            self._video_selected(file)

    def _open_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta", self.out_edit.text())
        if d:
            self.out_edit.setText(d)

    def _start(self):
        if not self.output_folder:
            QMessageBox.critical(self, "Error", "No se ha seleccionado ningún vídeo o la ruta de salida es inválida.")
            return
            
        os.makedirs(self.output_folder, exist_ok=True)
        params = {
            'video_path': self.video_path,
            'output_dir': self.output_folder,
            'sample_rate': self.sample.value(),
            'rotate': int(self.rotate.currentText()),
            'target_width': self.wi.value(),
            'target_height': self.he.value(),
            'normalize': self.norm.isChecked()
        }
        self.worker = WorkerThread(**params)
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.error_signal.connect(lambda e: QMessageBox.critical(self, "Error", e))
        self.worker.finished_signal.connect(lambda m: QMessageBox.information(
            self, "Finalizado", f"Procesados {m['frames_saved']} frames\nSalida: {self.output_folder}"))
        self.process_btn.setEnabled(False)
        self.worker.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    load_stylesheet(app, dark=False)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())