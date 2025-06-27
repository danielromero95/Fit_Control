# src/gui/main_window.py

import os
import cv2
import logging
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QStackedWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QApplication,
    QButtonGroup,
)
from PyQt5.QtCore import Qt, QSettings, QByteArray
from PyQt5.QtGui import QPixmap, QImage, QTransform, QCloseEvent, QIcon
from typing import Dict, Any, Optional

import qtawesome as qta

import src.constants as app_constants
from src.gui.style_utils import load_stylesheet
from src.gui.worker import AnalysisWorker
from src.config import settings
from src import database
from .pages import (
    DashboardPage,
    ExercisesPage,
    ExerciseDetailPage,
    PlansPage,
    ProgressPage,
    SettingsPage,
    ContactPage,
    WebCalendarPage,
)

logger = logging.getLogger(__name__)

THEME_COLORS = {
    "dark": {"default": "#FFB74D", "checked": "#FFFFFF"},
    "light": {"default": "#FFFFFF", "checked": "#FFB74D"},
}

class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación. Orquesta todos los widgets y la interacción
    con el pipeline de análisis. Gestiona el estado de la GUI y las preferencias del usuario.
    """
    def __init__(self, project_root: str, translator, parent=None):
        """
        Constructor de la ventana principal.

        Args:
            project_root (str): Ruta raíz del proyecto para localizar recursos como hojas de estilo.
            translator: Instancia de ``Translator`` para localizar la interfaz.
        """
        super().__init__(parent)
        self.project_root = project_root
        print(f"DEBUG: Ruta Raíz del Proyecto detectada: {self.project_root}")
        self.translator = translator
        self.video_path: Optional[str] = None
        self.gui_settings: Dict[str, Any] = {}

        # Track current theme
        self._is_dark_theme: bool = True
        
        # QSettings se usa para guardar y cargar las preferencias del usuario entre sesiones.
        self.q_settings = QSettings(app_constants.ORGANIZATION_NAME, app_constants.APP_NAME)
        self.current_rotation: int = 0
        self.original_pixmap: Optional[QPixmap] = None
        self.current_exercise_name: Optional[str] = None

        self.setWindowTitle(app_constants.APP_NAME)
        self.setWindowIcon(QIcon('assets/FitControl_logo.ico'))
        self.resize(800, 750)
        
        self._init_ui()
        self._load_settings()
        self._apply_theme(self.settings_page.theme_combo.currentText() == "Oscuro")

    def _init_ui(self):
        """Construye e inicializa todos los componentes de la interfaz de usuario."""
        container = QWidget()
        main_layout = QHBoxLayout(container)

        self.nav_widget = QWidget()
        self.nav_widget.setObjectName("navPanel")
        self.nav_widget.setMinimumWidth(130)
        self.nav_layout = QVBoxLayout(self.nav_widget)
        self.nav_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_layout.setSpacing(10)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.stack = QStackedWidget()

        # Páginas
        self.dashboard_page = DashboardPage()
        self.dashboard_page.exercise_selected.connect(self._on_exercise_by_name)
        self.exercises_page = ExercisesPage(project_root=self.project_root)
        self.exercises_page.exercise_selected.connect(self._on_exercise_selected)
        self.exercise_detail_page = ExerciseDetailPage(
            self._on_video_selected,
            self._on_rotation_requested,
            self._open_file_dialog,
            self._start_analysis,
        )
        self.progress_page = ProgressPage()
        self.results_panel = self.progress_page.results_panel
        calendar_html_path = os.path.join(
            self.project_root, "frontend", "index.html"
        )
        self.plans_page = WebCalendarPage(os.path.abspath(calendar_html_path))
        self.plans_page.exercise_selected.connect(self._on_exercise_by_name)
        self.settings_page = SettingsPage(self._apply_theme)
        self.contact_page = ContactPage()

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.exercises_page)
        self.stack.addWidget(self.plans_page)
        self.stack.addWidget(self.progress_page)
        self.stack.addWidget(self.settings_page)
        self.stack.addWidget(self.contact_page)
        self.stack.addWidget(self.exercise_detail_page)

        # Botones de navegación
        self.nav_buttons = []
        buttons = [
            ("fa5s.tachometer-alt", "Inicio", "Ir a la sección de Dashboard"),
            ("fa5s.dumbbell", "Ejercicios", "Explorar biblioteca de ejercicios"),
            ("fa5s.calendar-alt", "Planes", "Gestionar tus planes de entrenamiento"),
            ("fa5s.chart-line", "Progreso", "Consultar historial de análisis"),
            ("fa5s.cog", "Ajustes", "Abrir ajustes de la aplicación"),
        ]
        for idx, (icon_name, text, tip) in enumerate(buttons):
            btn = self._create_nav_button(icon_name, text, idx, tip)
            self.nav_buttons.append(btn)

        self.nav_layout.addStretch(1)

        contact_index = self.stack.indexOf(self.contact_page)
        contact_btn = self._create_nav_button("fa5s.info-circle", "Contacto", contact_index, "Información de contacto")
        self.nav_buttons.append(contact_btn)

        main_layout.addWidget(self.nav_widget)
        main_layout.addWidget(self.stack, 1)

        self.setCentralWidget(container)
        self._navigate(0)

    def _navigate(self, index: int):
        """Cambia la página visible en el stacked widget y actualiza los botones."""
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(getattr(self, "nav_buttons", [])):
            btn.setChecked(i == index)
        if index == self.stack.indexOf(self.progress_page):
            self.progress_page.refresh_analysis_list(
                self.progress_page.exercise_combo.currentText()
            )
        if index == self.stack.indexOf(self.dashboard_page):
            self.dashboard_page.refresh_dashboard()
        w = self.stack.currentWidget()
        w.update()
        w.repaint()
        self._update_nav_icons()

    def _create_nav_button(self, icon_name: str, text: str, page_index: int, tooltip: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("navButton")
        btn.setIcon(qta.icon(icon_name))
        btn.setProperty("icon_name", icon_name)  # Store for theme updates
        btn.setCheckable(True)
        btn.setToolTip(tooltip)
        btn.setStyleSheet("text-align: left; padding-left: 10px;")
        self.nav_group.addButton(btn, page_index)
        btn.clicked.connect(lambda _: self._navigate(page_index))
        self.nav_layout.addWidget(btn)
        return btn

    def _update_nav_icons(self) -> None:
        """Repaint navigation icons using the centralized theme color config."""
        theme_name = "dark" if self._is_dark_theme else "light"
        colors = THEME_COLORS[theme_name]

        default_color = colors["default"]
        checked_color = colors["checked"]

        for btn in getattr(self, "nav_buttons", []):
            icon_name = btn.property("icon_name")
            if icon_name:
                color = checked_color if btn.isChecked() else default_color
                btn.setIcon(qta.icon(icon_name, color=color))

    def _on_exercise_selected(self, exercise_id: int) -> None:
        """Carga el detalle del ejercicio seleccionado y navega a la vista."""
        row = database.get_exercise_by_id(exercise_id)
        if row:
            self.current_exercise_name = row.get("name")
        self.exercise_detail_page.load_exercise(exercise_id)
        self._navigate(self.stack.indexOf(self.exercise_detail_page))

    def _on_exercise_by_name(self, name: str) -> None:
        row = database.get_exercise_by_name(name)
        if row:
            self._on_exercise_selected(int(row["id"]))

    

    def _apply_theme(self, is_dark: bool):
        """Aplica el tema actual a todos los componentes relevantes de la GUI."""
        self._is_dark_theme = is_dark
        load_stylesheet(QApplication.instance(), self.project_root, dark=is_dark)

        # Refresh icons with new theme colors
        self._update_nav_icons()

        if hasattr(self, 'progress_page'):
            self.progress_page.set_theme(is_dark)

    def _on_video_selected(self, path: str):
        """
        Manejador para cuando se selecciona un nuevo vídeo, ya sea por diálogo o drag & drop.
        Actualiza la previsualización y resetea el estado de la aplicación.
        """
        self.video_path = path
        self.current_rotation = 0
        self.exercise_detail_page.analysis_page.results_label.setText(
            f"Vídeo cargado: {os.path.basename(path)}"
        )
        
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
        
        self.exercise_detail_page.analysis_page.process_btn.setEnabled(True)
        self.exercise_detail_page.analysis_page.progress_bar.setValue(0)
        self.progress_page.clear_results()
        # Deshabilitamos el acceso a la página de progreso hasta tener resultados
        if len(self.nav_buttons) > 3:
            self.nav_buttons[3].setEnabled(False)
        self._navigate(self.stack.indexOf(self.exercise_detail_page))
        
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
        self.exercise_detail_page.analysis_page.video_display.set_thumbnail(
            rotated_pixmap.scaled(
                self.exercise_detail_page.analysis_page.video_display.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    def _start_analysis(self):
        """Recoge los ajustes de la GUI e inicia el análisis en un hilo separado."""
        if not self.video_path:
            QMessageBox.critical(self, "Error", "No se ha seleccionado ningún vídeo."); return
        
        gui_settings = {
            "output_dir": self.settings_page.output_dir_edit.text().strip(),
            "sample_rate": self.settings_page.sample_rate_spin.value(),
            "rotate": self.current_rotation,
            "dark_mode": self.settings_page.theme_combo.currentText() == "Oscuro",
            "exercise": self.current_exercise_name or next(iter(settings.exercises)),
            "video_path": self.video_path,
        }

        self.gui_settings = gui_settings
        self.worker = AnalysisWorker(self.video_path, gui_settings)
        self.worker.progress.connect(self.exercise_detail_page.analysis_page.progress_bar.setValue)
        self.worker.error.connect(self._on_processing_error)
        self.worker.finished.connect(self._on_processing_finished)
        
        self._set_processing_state(True)
        self.worker.start()
        
    def _set_processing_state(self, is_processing: bool):
        """Habilita o deshabilita los controles de la GUI durante el análisis."""
        is_enabled = not is_processing
        # Bloqueamos la sección de Ajustes mientras se procesa
        if len(self.nav_buttons) > 4:
            self.nav_buttons[4].setEnabled(is_enabled)
        self.exercise_detail_page.analysis_page.process_btn.setEnabled(
            is_enabled and self.video_path is not None
        )
        if is_processing:
            self.exercise_detail_page.analysis_page.results_label.setText("Procesando... por favor, espere.")
        else:
            self.exercise_detail_page.analysis_page.results_label.setText("Análisis finalizado.")

    def _on_processing_error(self, error_message: str):
        """Slot que se activa si el hilo de análisis emite un error."""
        QMessageBox.critical(self, "Error de Procesamiento", error_message)
        self._set_processing_state(False)

    def _on_processing_finished(self, results: Dict[str, Any]):
        """Slot que se activa cuando el análisis termina con éxito."""
        self._set_processing_state(False)
        try:
            database.save_analysis_results(results, getattr(self, 'gui_settings', {}))
            self.statusBar().showMessage("Resultados guardados en la base de datos", 5000)
        except Exception as e:
            logger.error(f"Error guardando resultados en DB: {e}")

        rep_count = results.get("repeticiones_contadas", "N/A")
        self.exercise_detail_page.analysis_page.results_label.setText(
            f"¡Análisis Completo! Repeticiones: {rep_count}"
        )
        
        if len(self.nav_buttons) > 3:
            self.nav_buttons[3].setEnabled(True)
        self.progress_page.update_results(results)
        self._navigate(3)
    
    def _load_settings(self):
        """Carga las preferencias del usuario guardadas en la sesión anterior."""
        self.settings_page.output_dir_edit.setText(
            self.q_settings.value(
                "output_dir", os.path.join(self.project_root, "data", "processed")
            )
        )
        self.settings_page.sample_rate_spin.setValue(
            self.q_settings.value(
                "sample_rate", app_constants.DEFAULT_SAMPLE_RATE, type=int
            )
        )

        geometry = self.q_settings.value("geometry", QByteArray())
        if isinstance(geometry, QByteArray) and not geometry.isEmpty():
            self.restoreGeometry(geometry)

        # Siempre empezamos en el dashboard
        is_dark = self.q_settings.value(
            "dark_mode", app_constants.DEFAULT_DARK_MODE, type=bool
        )
        self.settings_page.theme_combo.setCurrentText("Oscuro" if is_dark else "Claro")

        # Aplicamos el tema explícitamente al arrancar
        self._apply_theme(is_dark)
        self._navigate(0)

    def closeEvent(self, event: QCloseEvent):
        """Guarda las preferencias del usuario al cerrar la aplicación."""
        self.q_settings.setValue(
            "output_dir", self.settings_page.output_dir_edit.text()
        )
        self.q_settings.setValue(
            "sample_rate", self.settings_page.sample_rate_spin.value()
        )
        self.q_settings.setValue(
            "dark_mode", self.settings_page.theme_combo.currentText() == "Oscuro"
        )
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
