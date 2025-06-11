# --------------------------------------------------------
# Archivo: frame_extraction_gui.py
# --------------------------------------------------------
"""
Interfaz gráfica (PyQt5) unificada para:
  1) Extraer fotogramas (muestra cada N, rota).
  2) Preprocesar cada frame (redimensionar y normalizar).
Mostramos logs en tiempo real y guardamos los resultados en una sola carpeta.
"""

import sys
import os
import logging
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QFileDialog,
    QSpinBox,
    QComboBox,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QHBoxLayout,
    QFormLayout,
    QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from frame_extraction import extract_and_preprocess_frames  # Importa la función unificada


# --------------------------------------------------------
# Logging handler que envía mensajes a un QTextEdit
# --------------------------------------------------------
class QTextEditLogger(QObject, logging.Handler):
    sigLog = pyqtSignal(str)

    def __init__(self, parent):
        QObject.__init__(self)
        logging.Handler.__init__(self)
        self.widget = parent

    def emit(self, record):
        msg = self.format(record)
        self.sigLog.emit(msg)


# --------------------------------------------------------
# WorkerThread para ejecutar extract_and_preprocess_frames sin bloquear la GUI
# --------------------------------------------------------
class WorkerThread(QThread):
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    log_signal = pyqtSignal(str)

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
            self.log_signal.emit("Iniciando extracción + preprocesamiento en segundo plano...\n")
            metadata = extract_and_preprocess_frames(
                video_path=self.video_path,
                output_dir=self.output_dir,
                sample_rate=self.sample_rate,
                rotate=self.rotate,
                target_width=self.target_width,
                target_height=self.target_height,
                normalize=self.normalize
            )
            self.log_signal.emit("Proceso finalizado sin errores.\n")
            self.finished_signal.emit(metadata)
        except Exception as e:
            self.log_signal.emit(f"Error durante el proceso:\n{str(e)}\n")
            self.error_signal.emit(str(e))


# --------------------------------------------------------
# Ventana principal de la GUI
# --------------------------------------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Extracción + Preprocesamiento de Fotogramas")
        self.setMinimumSize(650, 550)
        self._setup_ui()
        self._setup_logging()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # --- Determinar rutas por defecto relativas a este script ---
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.default_input = os.path.join(base_dir, "data", "raw", "own_videos")
        self.default_output = os.path.join(base_dir, "data", "processed", "frames")

        # ───────────────────────────────────────────────────────────────────────
        # Formulario de selección: Vídeo + Carpeta + Sample + Rotar + Width/Height + Normalize
        # ───────────────────────────────────────────────────────────────────────
        form_layout = QFormLayout()

        # 1) Vídeo de entrada (solo carpeta como placeholder, luego se elige archivo)
        self.txt_video = QLineEdit(self.default_input)
        self.txt_video.setReadOnly(True)
        btn_browse_video = QPushButton("Seleccionar vídeo")
        btn_browse_video.clicked.connect(self._browse_video)
        h_video = QHBoxLayout()
        h_video.addWidget(self.txt_video)
        h_video.addWidget(btn_browse_video)
        form_layout.addRow(QLabel("Vídeo de entrada:"), h_video)

        # 2) Carpeta de salida
        self.txt_output = QLineEdit(self.default_output)
        self.txt_output.setReadOnly(True)
        btn_browse_output = QPushButton("Seleccionar carpeta")
        btn_browse_output.clicked.connect(self._browse_output)
        h_output = QHBoxLayout()
        h_output.addWidget(self.txt_output)
        h_output.addWidget(btn_browse_output)
        form_layout.addRow(QLabel("Carpeta de salida:"), h_output)

        # 3) Sample Rate (cada N fotogramas)
        self.spin_sample = QSpinBox()
        self.spin_sample.setMinimum(1)
        self.spin_sample.setValue(3)
        form_layout.addRow(QLabel("Sample Rate (cada N fotogramas):"), self.spin_sample)

        # 4) Rotar fotogramas
        self.combo_rotate = QComboBox()
        self.combo_rotate.addItems(["0", "90", "180", "270"])
        self.combo_rotate.setCurrentText("90")  # rotación por defecto
        form_layout.addRow(QLabel("Rotar fotogramas (grados):"), self.combo_rotate)

        # 5) Ancho final
        self.spin_width = QSpinBox()
        self.spin_width.setMinimum(16)
        self.spin_width.setMaximum(4096)
        self.spin_width.setValue(256)
        form_layout.addRow(QLabel("Ancho final (px):"), self.spin_width)

        # 6) Alto final
        self.spin_height = QSpinBox()
        self.spin_height.setMinimum(16)
        self.spin_height.setMaximum(4096)
        self.spin_height.setValue(256)
        form_layout.addRow(QLabel("Alto final (px):"), self.spin_height)

        # 7) Checkbox Normalizar
        self.check_normalize = QCheckBox("Normalizar valores 0–255 → 0.0–1.0 → 0–255")
        form_layout.addRow(self.check_normalize)

        layout.addLayout(form_layout)

        # 8) Botón de iniciar TODO
        self.btn_start = QPushButton("Iniciar extracción + preprocesamiento")
        self.btn_start.clicked.connect(self._on_start)
        self.btn_start.setFixedHeight(36)
        layout.addWidget(self.btn_start)

        # 9) Área de texto para logs
        lbl_logs = QLabel("Logs de ejecución:")
        self.txt_logs = QTextEdit()
        self.txt_logs.setReadOnly(True)
        layout.addWidget(lbl_logs)
        layout.addWidget(self.txt_logs)

        self.setLayout(layout)

    def _setup_logging(self):
        # Conectar el root logger para que emita en el QTextEdit
        self.qt_handler = QTextEditLogger(self.txt_logs)
        self.qt_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S")
        self.qt_handler.setFormatter(formatter)
        self.qt_handler.sigLog.connect(self._append_log)
        logging.getLogger().addHandler(self.qt_handler)
        logging.getLogger().setLevel(logging.DEBUG)

    def _append_log(self, msg):
        cursor = self.txt_logs.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(msg + "\n")
        self.txt_logs.setTextCursor(cursor)
        self.txt_logs.ensureCursorVisible()

    def _browse_video(self):
        # Inicia el diálogo directamente en self.default_input
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de vídeo",
            self.default_input,
            "Vídeos (*.mp4 *.mov *.avi *.mkv *.mpg *.mpeg *.wmv)"
        )
        if file_path:
            self.txt_video.setText(file_path)

    def _browse_output(self):
        # Inicia el diálogo directamente en self.default_output
        folder = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta de salida",
            self.default_output
        )
        if folder:
            self.txt_output.setText(folder)

    def _on_start(self):
        video_path = self.txt_video.text().strip()
        output_dir = self.txt_output.text().strip()
        sample_rate = self.spin_sample.value()
        rotate = int(self.combo_rotate.currentText())
        target_width = self.spin_width.value()
        target_height = self.spin_height.value()
        normalize = self.check_normalize.isChecked()

        # Validaciones
        if not video_path or not os.path.isfile(video_path):
            QMessageBox.warning(self, "Falta vídeo", "Por favor, selecciona un archivo de vídeo válido.")
            return
        if not output_dir:
            QMessageBox.warning(self, "Falta carpeta de salida", "Por favor, selecciona una carpeta de salida.")
            return

        # Si la carpeta de salida no existe, solicitar creación
        if not os.path.isdir(output_dir):
            respuesta = QMessageBox.question(
                self, "Carpeta no existe",
                f"La carpeta \"{output_dir}\" no existe.\n¿Deseas crearla?",
                QMessageBox.Yes | QMessageBox.No
            )
            if respuesta == QMessageBox.Yes:
                try:
                    os.makedirs(output_dir, exist_ok=True)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo crear la carpeta:\n{e}")
                    return
            else:
                return

        # Deshabilitar botón y limpiar logs
        self.btn_start.setEnabled(False)
        self.txt_logs.clear()

        # Lanzar WorkerThread con todos los parámetros
        self.worker = WorkerThread(
            video_path,
            output_dir,
            sample_rate,
            rotate,
            target_width,
            target_height,
            normalize
        )
        self.worker.log_signal.connect(self._append_log)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.error_signal.connect(self._on_error)
        self.worker.start()

    def _on_finished(self, metadata):
        QMessageBox.information(
            self, "Finalizado",
            ("Extracción + Preprocesamiento completados:\n"
             f"- FPS: {metadata['fps']:.2f}\n"
             f"- Total fotogramas: {metadata['frame_count']}\n"
             f"- Duración (s): {metadata['duration']:.2f}\n"
             f"- Fotogramas guardados: {metadata['frames_saved']}")
        )
        self.btn_start.setEnabled(True)

    def _on_error(self, err_msg):
        QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{err_msg}")
        self.btn_start.setEnabled(True)


# --------------------------------------------------------
# Iniciar la app PyQt5
# --------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
