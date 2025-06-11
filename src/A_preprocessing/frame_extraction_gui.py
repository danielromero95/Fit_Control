import sys
import os
import logging
import cv2
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QLineEdit,
    QFileDialog, QSpinBox, QComboBox, QCheckBox, QVBoxLayout,
    QHBoxLayout, QTabWidget, QMessageBox, QProgressBar, QFormLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from frame_extraction import extract_and_preprocess_frames


class DragDropWidget(QWidget):
    file_dropped = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.label = QLabel("Arrastra y suelta tu vídeo aquí")
        self.label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setStyleSheet(
            "QWidget { border: 2px dashed #aaa; border-radius: 8px; } QLabel { color: #555; font-size: 16px; }"
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
                if idx % step == 0:
                    percent = int(idx / frame_count * 100)
                    self.progress_signal.emit(percent)
            cap.release()
            self.progress_signal.emit(100)
            metadata = {'fps': fps, 'frame_count': frame_count, 'duration': frame_count/fps if fps else 0, 'frames_saved': saved}
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
        tabs.addTab(self._build_home_tab(), "Inicio")
        tabs.addTab(self._build_settings_tab(), "Ajustes")
        self.setCentralWidget(tabs)

    def _build_home_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.drag_widget = DragDropWidget()
        self.drag_widget.file_dropped.connect(self._on_video_selected)
        layout.addWidget(self.drag_widget)

        btn_select = QPushButton("Seleccionar vídeo")
        btn_select.clicked.connect(self._browse_video)
        layout.addWidget(btn_select)

        # Thumbnail preview
        self.thumbnail = QLabel()
        self.thumbnail.setAlignment(Qt.AlignCenter)
        self.thumbnail.setFixedSize(320, 180)
        layout.addWidget(self.thumbnail)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.btn_process = QPushButton("Procesar vídeo")
        self.btn_process.clicked.connect(self._start_processing)
        self.btn_process.setEnabled(False)
        layout.addWidget(self.btn_process)

        widget.setLayout(layout)
        return widget

    def _build_settings_tab(self):
        widget = QWidget()
        layout = QFormLayout()

        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.edit_output = QLineEdit(os.path.join(base, 'data', 'processed', 'frames'))
        btn_out = QPushButton("...")
        btn_out.clicked.connect(self._browse_output)
        hb_out = QHBoxLayout()
        hb_out.addWidget(self.edit_output)
        hb_out.addWidget(btn_out)
        layout.addRow("Carpeta de salida:", hb_out)

        self.spin_sample = QSpinBox()
        self.spin_sample.setMinimum(1)
        self.spin_sample.setValue(3)
        layout.addRow("Sample Rate:", self.spin_sample)

        self.combo_rotate = QComboBox()
        self.combo_rotate.addItems(["0","90","180","270"])
        self.combo_rotate.setCurrentText("90")
        layout.addRow("Rotación (°):", self.combo_rotate)

        self.spin_width = QSpinBox()
        self.spin_width.setRange(16,4096)
        self.spin_width.setValue(256)
        layout.addRow("Ancho (px):", self.spin_width)

        self.spin_height = QSpinBox()
        self.spin_height.setRange(16,4096)
        self.spin_height.setValue(256)
        layout.addRow("Alto (px):", self.spin_height)

        self.chk_norm = QCheckBox("Normalizar")
        self.chk_norm.setToolTip("Escala los valores de píxel de 0–255 a 0.0–1.0 antes de guardar.")
        self.chk_norm.setChecked(True)
        layout.addRow(self.chk_norm)

        widget.setLayout(layout)
        return widget

    def _on_video_selected(self, path):
        self.video_path = path
        self.drag_widget.label.setText(os.path.basename(path))
        cap = cv2.VideoCapture(path)
        ret, frame = cap.read()
        cap.release()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            ratio = min(self.thumbnail.width()/w, self.thumbnail.height()/h)
            thumb = cv2.resize(frame, (int(w*ratio), int(h*ratio)))
            image = QImage(thumb.data, thumb.shape[1], thumb.shape[0], thumb.strides[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.thumbnail.setPixmap(pixmap)
        self.btn_process.setEnabled(True)

    def _browse_video(self):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw', 'own_videos'))
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar vídeo", base, "Vídeos (*.mp4 *.mov *.avi *.mkv)")
        if file_path:
            self._on_video_selected(file_path)

    def _browse_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta", self.edit_output.text())
        if folder:
            self.edit_output.setText(folder)

    def _start_processing(self):
        if not hasattr(self, 'video_path'):
            return
        out = self.edit_output.text().strip()
        os.makedirs(out, exist_ok=True)
        params = dict(
            video_path=self.video_path,
            output_dir=out,
            sample_rate=self.spin_sample.value(),
            rotate=int(self.combo_rotate.currentText()),
            target_width=self.spin_width.value(),
            target_height=self.spin_height.value(),
            normalize=self.chk_norm.isChecked()
        )
        self.worker = WorkerThread(**params)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.error_signal.connect(lambda e: QMessageBox.critical(self, "Error", e))
        self.worker.finished_signal.connect(self._on_finished)
        self.btn_process.setEnabled(False)
        self.worker.start()

    def _on_finished(self, metadata):
        QMessageBox.information(self, "Finalizado",
            f"Procesados {metadata['frames_saved']} frames en {metadata['duration']:.1f}s")
        self.btn_process.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
