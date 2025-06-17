# src/gui/widgets/results_panel.py

import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QFrame, QCheckBox, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QMediaPlayer
from typing import Dict # <-- 1. IMPORTACIÓN AÑADIDA

from .plot_widget import PlotWidget
from .video_player import VideoPlayerWidget

logger = logging.getLogger(__name__)

class ResultsPanel(QWidget):
    """
    Panel que muestra los resultados del análisis: vídeo, contador de repeticiones,
    gráficos interactivos y lista de fallos. Orquesta la interacción entre widgets.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fps: float = 30.0
        self.checkboxes: Dict[str, QCheckBox] = {}
        self.init_ui()

    def init_ui(self):
        """Inicializa y organiza todos los widgets de la interfaz."""
        main_layout = QHBoxLayout(self)

        # --- Columna Izquierda ---
        self.video_player = VideoPlayerWidget(self)
        main_layout.addWidget(self.video_player, 2)
        
        # --- Columna Derecha ---
        right_column_widget = QWidget()
        right_column_layout = QVBoxLayout(right_column_widget)
        
        # Sección superior: Repeticiones y Estado
        top_layout = QHBoxLayout()
        self.rep_counter = QLabel("0"); font = self.rep_counter.font(); font.setPointSize(48); font.setBold(True)
        self.rep_counter.setFont(font); self.rep_counter.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self._create_box("Repeticiones", self.rep_counter))

        self.status_label = QLabel("Listo"); font = self.status_label.font(); font.setPointSize(12)
        self.status_label.setFont(font); self.status_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self._create_box("Estado", self.status_label))
        right_column_layout.addLayout(top_layout)
        
        # Widget del Gráfico
        self.plot_widget = PlotWidget(self)
        self.plot_widget.frame_clicked_signal.connect(self.on_frame_selected)
        right_column_layout.addWidget(self.plot_widget)
        
        # Sección de controles de visibilidad para las curvas
        self.visibility_group = QGroupBox("Curvas Visibles")
        visibility_layout = QHBoxLayout()
        for display_name in self.plot_widget.CURVE_MAP.values():
            cb = QCheckBox(display_name)
            cb.toggled.connect(self._update_curve_visibility)
            visibility_layout.addWidget(cb)
            self.checkboxes[display_name] = cb
        self.visibility_group.setLayout(visibility_layout)
        right_column_layout.addWidget(self.visibility_group)
        
        # Sección de fallos
        faults_label = QLabel("Fallos Detectados:"); font = faults_label.font(); font.setBold(True)
        faults_label.setFont(font); right_column_layout.addWidget(faults_label)
        self.fault_list = QListWidget(self); right_column_layout.addWidget(self.fault_list)

        main_layout.addWidget(right_column_widget, 1)
        
        # Limpiamos y ocultamos los elementos dinámicos al inicio
        self.clear_results()

    def on_frame_selected(self, frame_index: int):
        """Slot que se activa al hacer clic en el gráfico para saltar en el vídeo."""
        if self.video_player.media_player.isSeekable():
            position_ms = (frame_index / self.fps) * 1000
            self.video_player.set_position(int(position_ms))
        else:
            logger.warning("Intento de buscar en el vídeo, pero no está listo (seekable).")

    def _update_curve_visibility(self):
        """Notifica al PlotWidget qué curvas mostrar u ocultar según los checkboxes."""
        for display_name, checkbox in self.checkboxes.items():
            self.plot_widget.set_curve_visibility(display_name, checkbox.isChecked())

    def update_results(self, results: Dict):
        """Rellena todos los widgets con los nuevos resultados del pipeline."""
        self.clear_results()
        
        self.rep_counter.setText(str(results.get("repeticiones_contadas", "0")))
        self.fps = results.get("fps", 30.0)
        df = results.get("dataframe_metricas")
        
        if df is None or df.empty:
            self.status_label.setText("Estado: No se generaron métricas."); return

        self.status_label.setText("Estado: Análisis completado.")
        self.plot_widget.plot_data(df)
        
        # Muestra los checkboxes solo para las curvas que tienen datos
        curves_found = self.plot_widget._plotted_curves.keys()
        any_cb_visible = False
        for display_name, checkbox in self.checkboxes.items():
            is_visible = display_name in curves_found
            checkbox.setVisible(is_visible)
            checkbox.setChecked(is_visible)
            if is_visible: any_cb_visible = True
        self.visibility_group.setVisible(any_cb_visible)
        
        # Actualiza la lista de fallos
        faults = results.get("fallos_detectados", [])
        self.fault_list.clear()
        if not faults:
            self.fault_list.addItem("¡No se detectaron fallos!")
        
        # Añadimos el mensaje contextual si solo se ve una pierna
        if len(curves_found) == 1:
            self.fault_list.addItem(f"Info: Solo se detectó la '{list(curves_found)[0]}'.")

        for fault in faults:
            self.fault_list.addItem(f"Rep {fault['rep']}: {fault['type']} ({fault['value']})")
        
        # Carga el vídeo al final
        video_path = results.get("debug_video_path")
        if video_path:
            self.video_player.load_video(video_path)

    def _create_box(self, title: str, widget: QWidget) -> QFrame:
        """Función helper para crear cajas con título y borde."""
        box = QFrame(); box.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(box)
        title_label = QLabel(title); font = title_label.font(); font.setBold(True)
        title_label.setFont(font); title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label); layout.addWidget(widget)
        return box
    
    def clear_results(self):
        """Limpia todos los resultados para un nuevo análisis."""
        self.rep_counter.setText("0")
        self.status_label.setText("Listo para analizar")
        self.plot_widget.clear_plots()
        self.fault_list.clear()
        self.video_player.clear_media()
        self.visibility_group.hide()