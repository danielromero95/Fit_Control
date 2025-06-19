# src/gui/main_window.py

import os
import cv2
import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QTabWidget, QVBoxLayout, QFormLayout, 
                             QHBoxLayout, QPushButton, QProgressBar, QLabel, QSpinBox, 
                             QCheckBox, QLineEdit, QFileDialog, QMessageBox, QApplication)
from PyQt5.QtCore import Qt, QSettings, QByteArray
from PyQt5.QtGui import QPixmap, QImage, QFont, QTransform, QCloseEvent
from typing import Dict, Any, Optional, Callable

import src.constants as app_constants
from src.gui.style_utils import load_stylesheet
from src.gui.widgets.video_display import VideoDisplayWidget
from .widgets.results_panel import ResultsPanel
from src.gui.worker import AnalysisWorker

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación. Orquesta todos los widgets y la interacción
    con el pipeline de análisis. Gestiona el estado de la GUI y las preferencias del usuario.
    """
    def __init__(self, project_root: str, parent=None):
        """
        Constructor de la ventana principal.
        
        Args:
            project_root (str): Ruta raíz del proyecto para localizar recursos como hojas de estilo.
        """
        super().__init__(parent)
        self.project_root = project_root
        self.video_path: Optional[str] = None
        
        # QSettings se usa para guardar y cargar las preferencias del usuario entre sesiones.
        self.q_settings = QSettings(app_constants.ORGANIZATION_NAME, app_constants.APP_NAME)
        self.current_rotation: int = 0
        self.original_pixmap: Optional[QPixmap] = None

        self.setWindowTitle(app_constants.APP_NAME)
        self.resize(800, 750)
        
        self._init_ui()
        self._load_settings()
        self._apply_theme(self.dark_mode_check.isChecked())

    def _init_ui(self):
        """Construye e inicializa todos los componentes de la interfaz de usuario."""
        self.tabs = QTabWidget()
        # Conectar para refrescar al cambiar de pestaña
        self.tabs.currentChanged.connect(self._on_tab_changed)

        # Pestaña Inicio
        home = self._create_home_tab()
        home.setAutoFillBackground(True)
        self.tabs.addTab(home, "Inicio")
        
        # Pestaña Resultados
        self.results_panel = ResultsPanel(self)
        self.results_panel.setAutoFillBackground(True)
        self.tabs.addTab(self.results_panel, "Resultados")
        self.tabs.setTabEnabled(1, False)

        # Pestaña Ajustes
        settings_tab = self._create_settings_tab()
        settings_tab.setAutoFillBackground(True)
        self.tabs.addTab(settings_tab, "Ajustes")

        self.setCentralWidget(self.tabs)

    def _create_home_tab(self) -> QWidget:
        """Crea y devuelve el widget para la pestaña 'Inicio'."""
        widget = QWidget(); layout = QVBoxLayout(widget)
        
        video_container = QWidget(); video_container.setFixedHeight(400)
        video_container_layout = QVBoxLayout(video_container); video_container_layout.setContentsMargins(0,0,0,0)
        
        self.video_display = VideoDisplayWidget()
        self.video_display.file_dropped.connect(self._on_video_selected)
        self.video_display.rotation_requested.connect(self._on_rotation_requested)
        video_container_layout.addWidget(self.video_display)
        layout.addWidget(video_container)
        
        self.select_video_btn = QPushButton("Seleccionar Vídeo..."); self.select_video_btn.clicked.connect(self._open_file_dialog)
        layout.addWidget(self.select_video_btn)

        self.progress_bar = QProgressBar(); layout.addWidget(self.progress_bar)
        
        self.results_label = QLabel("Arrastra un vídeo o selecciónalo para empezar"); self.results_label.setAlignment(Qt.AlignCenter)
        font = QFont(); font.setPointSize(12); self.results_label.setFont(font)
        layout.addWidget(self.results_label)
        
        self.process_btn = QPushButton("Analizar Vídeo"); self.process_btn.setEnabled(False); self.process_btn.clicked.connect(self._start_analysis)
        layout.addWidget(self.process_btn)
        
        return widget

    def _create_settings_tab(self) -> QWidget:
        """Crea y devuelve el widget para la pestaña 'Ajustes'."""
        widget = QWidget(); layout = QFormLayout(widget)
        
        self.output_dir_edit = QLineEdit()
        self.sample_rate_spin = QSpinBox(); self.sample_rate_spin.setMinimum(1)
        
        self.dark_mode_check = QCheckBox("Modo Oscuro")
        # Usamos la señal 'toggled(bool)' que es más directa y limpia para este caso.
        self.dark_mode_check.toggled.connect(self._apply_theme)

        layout.addRow("Carpeta de Salida:", self.output_dir_edit)
        layout.addRow("Sample Rate (procesar 1 de cada N frames):", self.sample_rate_spin)
        layout.addRow(self.dark_mode_check)
        
        return widget
    
    def _on_tab_changed(self, index: int):
        """Forzar repintado al cambiar de pestaña."""
        w = self.tabs.widget(index)
        w.update()
        w.repaint()

    def _apply_theme(self, is_dark: bool):
        """Aplica el tema actual a todos los componentes relevantes de la GUI."""
        load_stylesheet(QApplication.instance(), self.project_root, dark=is_dark)
        if hasattr(self, 'results_panel'):
            self.results_panel.plot_widget.set_theme(is_dark)

    def _on_video_selected(self, path: str):
        """
        Manejador para cuando se selecciona un nuevo vídeo, ya sea por diálogo o drag & drop.
        Actualiza la previsualización y resetea el estado de la aplicación.
        """
        self.video_path = path
        self.current_rotation = 0
        self.results_label.setText(f"Vídeo cargado: {os.path.basename(path)}")
        
        try:
            from src.A_preprocessing.video_metadata import get_video_rotation
            self.current_rotation = get_video_rotation(path) or app_constants.DEFAULT_ROTATE
        except Exception as e:
            logger.error(f"Fallo en autodetección de rotación: {e}"); self.current_rotation = 0

        cap = cv2.VideoCapture(path); ret, frame = cap.read(); cap.release()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.original_pixmap = QPixmap.fromImage(QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], frame_rgb.strides[0], QImage.Format_RGB888))
            self._update_thumbnail()
        
        self.process_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.results_panel.clear_results()
        self.tabs.setTabEnabled(1, False)
        # Mejora de UX: Vuelve siempre a la pestaña 'Inicio'
        self.tabs.setCurrentIndex(0)
        
    def _on_rotation_requested(self, angle: int):
        """Manejador para la rotación manual de la previsualización del vídeo."""
        if self.original_pixmap is None: return
        self.current_rotation = (self.current_rotation + angle) % 360
        self._update_thumbnail()

    def _update_thumbnail(self):
        """Actualiza la imagen de previsualización con la rotación actual."""
        if self.original_pixmap is None: return
        transform = QTransform().rotate(self.current_rotation)
        rotated_pixmap = self.original_pixmap.transformed(transform)
        self.video_display.set_thumbnail(rotated_pixmap.scaled(self.video_display.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def _start_analysis(self):
        """Recoge los ajustes de la GUI e inicia el análisis en un hilo separado."""
        if not self.video_path:
            QMessageBox.critical(self, "Error", "No se ha seleccionado ningún vídeo."); return
        
        gui_settings = {
            'output_dir': self.output_dir_edit.text().strip(),
            'sample_rate': self.sample_rate_spin.value(),
            'rotate': self.current_rotation,
            'dark_mode': self.dark_mode_check.isChecked()
        }
        
        self.worker = AnalysisWorker(self.video_path, gui_settings)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.error.connect(self._on_processing_error)
        self.worker.finished.connect(self._on_processing_finished)
        
        self._set_processing_state(True)
        self.worker.start()
        
    def _set_processing_state(self, is_processing: bool):
        """Habilita o deshabilita los controles de la GUI durante el análisis."""
        is_enabled = not is_processing
        # Bloqueamos todas las pestañas que no sean la de Inicio para evitar cambios
        self.tabs.setTabEnabled(2, is_enabled) # Ajustes
        self.process_btn.setEnabled(is_enabled and self.video_path is not None)
        if is_processing:
            self.results_label.setText("Procesando... por favor, espere.")
        else:
            self.results_label.setText("Análisis finalizado.")

    def _on_processing_error(self, error_message: str):
        """Slot que se activa si el hilo de análisis emite un error."""
        QMessageBox.critical(self, "Error de Procesamiento", error_message)
        self._set_processing_state(False)

    def _on_processing_finished(self, results: Dict[str, Any]):
        """Slot que se activa cuando el análisis termina con éxito."""
        self._set_processing_state(False)
        rep_count = results.get("repeticiones_contadas", "N/A")
        self.results_label.setText(f"¡Análisis Completo! Repeticiones: {rep_count}")
        
        self.tabs.setTabEnabled(1, True)
        self.results_panel.update_results(results)
        self.tabs.setCurrentWidget(self.results_panel)
    
    def _load_settings(self):
        """Carga las preferencias del usuario guardadas en la sesión anterior."""
        self.output_dir_edit.setText(self.q_settings.value("output_dir", os.path.join(self.project_root, 'data', 'processed')))
        self.sample_rate_spin.setValue(self.q_settings.value("sample_rate", app_constants.DEFAULT_SAMPLE_RATE, type=int))
        
        geometry = self.q_settings.value("geometry", QByteArray())
        if isinstance(geometry, QByteArray) and not geometry.isEmpty():
            self.restoreGeometry(geometry)

        # Siempre empezamos en 'Inicio'
        self.dark_mode_check.setChecked(self.q_settings.value("dark_mode", app_constants.DEFAULT_DARK_MODE, type=bool))
        
        # Aplicamos el tema explícitamente al arrancar
        self._apply_theme(self.dark_mode_check.isChecked())

    def closeEvent(self, event: QCloseEvent):
        """Guarda las preferencias del usuario al cerrar la aplicación."""
        self.q_settings.setValue("output_dir", self.output_dir_edit.text())
        self.q_settings.setValue("sample_rate", self.sample_rate_spin.value())
        self.q_settings.setValue("dark_mode", self.dark_mode_check.isChecked())
        self.q_settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)

    def _open_file_dialog(self):
        """Abre el diálogo del sistema para seleccionar un fichero de vídeo."""
        default_input = os.path.dirname(self.video_path) if self.video_path else os.path.join(self.project_root, 'data', 'raw')
        wildcard_extensions = [f"*{ext}" for ext in app_constants.VIDEO_EXTENSIONS]
        filter_string = f"Vídeos ({' '.join(wildcard_extensions)})"
        file, _ = QFileDialog.getOpenFileName(self, "Seleccionar vídeo", default_input, filter_string)
        if file:
            self._on_video_selected(file)