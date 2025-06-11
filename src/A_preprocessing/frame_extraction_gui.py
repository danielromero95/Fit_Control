import sys
import os
import cv2
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QFileDialog, QSpinBox, QComboBox, QCheckBox, QVBoxLayout,
    QTabWidget, QMessageBox, QProgressBar, QFormLayout, QHBoxLayout, QLineEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from frame_extraction import extract_and_preprocess_frames


class DragDropWidget(QWidget):
    file_dropped = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.default_text = "Arrastra o selecciona tu vídeo aquí"
        self.label = QLabel(self.default_text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: #777; font-size: 16px;")
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setStyleSheet(
            "QWidget { border: 2px dashed #aaa; border-radius: 8px; }"
        )

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                self.file_dropped.emit(path)
                break

    def show_thumbnail(self, pixmap: QPixmap):
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)

    def clear(self):
        self.label.clear()
        self.label.setText(self.default_text)


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
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                raise IOError(f"No se pudo abrir el vídeo: {self.video_path}")

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
                    # rotate
                    if self.rotate == 90:
                        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                    elif self.rotate == 180:
                        frame = cv2.rotate(frame, cv2.ROTATE_180)
                    elif self.rotate == 270:
                        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    # resize
                    frame = cv2.resize(frame, (self.target_width, self.target_height), interpolation=cv2.INTER_AREA)
                    # normalize
                    if self.normalize:
                        frame = (frame.astype('float32') / 255.0 * 255.0).astype('uint8')
                    # save
                    fname = os.path.join(self.output_dir, f"frame_{saved+1:04d}.jpg")
                    cv2.imwrite(fname, frame)
                    saved += 1
                idx += 1
                if idx % step == 0:
                    percent = int(idx / frame_count * 100)
                    self.progress_signal.emit(percent)
            cap.release()
            self.progress_signal.emit(100)
            metadata = {
                'fps': fps,
                'frame_count': frame_count,
                'duration': frame_count/fps if fps else 0,
                'frames_saved': saved
            }
            self.finished_signal.emit(metadata)
        except Exception as e:
            self.error_signal.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gym Performance Analyzer")
        self.resize(700, 600)
        self._init_ui()

    def _init_ui(self):
        tabs = QTabWidget()
        tabs.addTab(self._home_tab(), "Inicio")
        tabs.addTab(self._settings_tab(), "Ajustes")
        self.setCentralWidget(tabs)

    def _home_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Drag & Drop area
        self.drag_widget = DragDropWidget()
        self.drag_widget.file_dropped.connect(self._video_selected)
        layout.addWidget(self.drag_widget)

        # Select button
        btn = QPushButton("Seleccionar vídeo")
        btn.clicked.connect(self._open_file)
        layout.addWidget(btn)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Process video button
        self.process_btn = QPushButton("Procesar vídeo")
        self.process_btn.setEnabled(False)
        self.process_btn.clicked.connect(self._start)
        layout.addWidget(self.process_btn)

        return widget

    def _settings_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

        # Output base folder
        self.out_edit = QLineEdit(os.path.join(base, 'data', 'processed', 'frames'))
        btn = QPushButton("...")
        btn.clicked.connect(self._open_dir)
        h = QHBoxLayout(); h.addWidget(self.out_edit); h.addWidget(btn)
        layout.addRow("Carpeta salida:", h)

        # Sample rate
        self.sample = QSpinBox(); self.sample.setMinimum(1); self.sample.setValue(3)
        layout.addRow("Sample Rate:", self.sample)

        # Rotation
        self.rotate = QComboBox(); self.rotate.addItems(["0","90","180","270"]); self.rotate.setCurrentText("90")
        layout.addRow("Rotación (°):", self.rotate)

        # Width/Height
        self.wi = QSpinBox(); self.wi.setRange(16,4096); self.wi.setValue(256)
        self.he = QSpinBox(); self.he.setRange(16,4096); self.he.setValue(256)
        layout.addRow("Ancho (px):", self.wi)
        layout.addRow("Alto (px):", self.he)

        # Normalize
        self.norm = QCheckBox("Normalizar")
        self.norm.setChecked(True)
        self.norm.setToolTip("Escala valor píxel de 0–255 a 0–1 antes de guardar.")
        layout.addRow(self.norm)

        return widget

    def _video_selected(self, path):
        self.video_path = path
        # create output subfolder named after video file (no extension)
        base_output = self.out_edit.text().strip()
        name = os.path.splitext(os.path.basename(path))[0]
        self.output_folder = os.path.join(base_output, name)
        # ensure fresh drag_widget
        cap = cv2.VideoCapture(path)
        ret, frame = cap.read()
        cap.release()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, _ = frame.shape
            dw, dh = self.drag_widget.size().width(), self.drag_widget.size().height()
            scale = min(dw/w, dh/h)
            thumb = cv2.resize(frame, (int(w*scale), int(h*scale)))
            img = QImage(thumb.data, thumb.shape[1], thumb.shape[0], thumb.strides[0], QImage.Format_RGB888)
            pix = QPixmap.fromImage(img)
            self.drag_widget.show_thumbnail(pix)
        self.process_btn.setEnabled(True)

    def _open_file(self):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw', 'own_videos'))
        file, _ = QFileDialog.getOpenFileName(self, "Seleccionar vídeo", base, "Vídeos (*.mp4 *.mov *.avi *.mkv)")
        if file:
            self.drag_widget.clear()
            self._video_selected(file)

    def _open_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta", self.out_edit.text())
        if d:
            self.out_edit.setText(d)

    def _start(self):
        # ensure output_folder created
        os.makedirs(self.output_folder, exist_ok=True)
        params = dict(
            video_path=self.video_path,
            output_dir=self.output_folder,
            sample_rate=self.sample.value(),
            rotate=int(self.rotate.currentText()),
            target_width=self.wi.value(),
            target_height=self.he.value(),
            normalize=self.norm.isChecked()
        )
        self.worker = WorkerThread(**params)
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.error_signal.connect(lambda e: QMessageBox.critical(self, "Error", e))
        self.worker.finished_signal.connect(lambda m: QMessageBox.information(self, "Finalizado", f"Procesados {m['frames_saved']} frames\nGuardados en el directorio: {self.output_folder}"))
        self.process_btn.setEnabled(False)
        self.worker.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow(); w.show(); sys.exit(app.exec_())
