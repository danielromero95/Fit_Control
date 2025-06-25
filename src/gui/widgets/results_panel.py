# src/gui/widgets/results_panel.py

import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QFrame, QCheckBox, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QMediaPlayer
from typing import Dict, Any, Optional

from .plot_widget import PlotWidget
from .video_player import VideoPlayerWidget

logger = logging.getLogger(__name__)

class ResultsPanel(QWidget):
    """
    Panel que muestra los resultados del análisis: vídeo, contador de repeticiones,
    gráficos interactivos y lista de fallos. Orquesta la interacción entre widgets.
    """
    def __init__(self, parent: Optional[QWidget] = None):
        """Inicializa el panel y sus componentes."""
        super().__init__(parent)
        self.fps: float = 30.0
        self.checkboxes: Dict[str, QCheckBox] = {}
        self.init_ui()

    def init_ui(self):
        """Inicializa y organiza todos los widgets de la interfaz."""
        main_layout = QHBoxLayout(self)

        # Columna Izquierda: Reproductor de Vídeo
        self.video_player = VideoPlayerWidget(self)
        main_layout.addWidget(self.video_player, 2)
        
        # Columna Derecha: Datos y Gráficos
        right_column_widget = QWidget()
        right_column_layout = QVBoxLayout(right_column_widget)
        
        top_layout = QHBoxLayout()
        self.rep_counter = QLabel("0")
        font_rep = QFont(); font_rep.setPointSize(48); font_rep.setBold(True)
        self.rep_counter.setFont(font_rep)
        self.rep_counter.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self._create_box("Repeticiones", self.rep_counter))

        self.status_label = QLabel("Listo")
        font_status = QFont(); font_status.setPointSize(12)
        self.status_label.setFont(font_status)
        self.status_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self._create_box("Estado", self.status_label))
        right_column_layout.addLayout(top_layout)
        
        # Widget del Gráfico
        self.plot_widget = PlotWidget(self)
        self.plot_widget.frame_clicked_signal.connect(self.on_frame_selected_from_plot)
        right_column_layout.addWidget(self.plot_widget)
        
        # Controles de Visibilidad de Curvas
        self.visibility_group = QGroupBox("Curvas Visibles")
        visibility_layout = QHBoxLayout()
        for display_name in self.plot_widget.CURVE_MAP.values():
            cb = QCheckBox(display_name)
            cb.toggled.connect(self._update_curve_visibility)
            visibility_layout.addWidget(cb)
            self.checkboxes[display_name] = cb
        self.visibility_group.setLayout(visibility_layout)
        right_column_layout.addWidget(self.visibility_group)
        
        # Lista de Fallos
        faults_label = QLabel("Fallos Detectados:")
        font_faults = QFont(); font_faults.setBold(True)
        faults_label.setFont(font_faults)
        right_column_layout.addWidget(faults_label)
        self.fault_list = QListWidget(self)
        right_column_layout.addWidget(self.fault_list)

        main_layout.addWidget(right_column_widget, 1)
        
        self.clear_results()

    def on_frame_selected_from_plot(self, frame_index: int) -> None:
        """Slot que se activa al hacer clic/arrastrar en el gráfico."""
        if self.video_player.media_player.isSeekable():
            # Desconectamos temporalmente para evitar un bucle de eventos
            try:
                self.video_player.media_player.positionChanged.disconnect(self.on_video_position_changed)
            except TypeError:
                pass # La señal ya estaba desconectada
            
            position_ms = (frame_index / self.fps) * 1000
            self.video_player.set_position_ms(int(position_ms))
            
            # Volvemos a conectar la señal
            self.video_player.media_player.positionChanged.connect(self.on_video_position_changed)
        else:
            logger.warning("Intento de buscar en el vídeo, pero no está listo (seekable).")
            
    def on_video_position_changed(self, position_ms: int) -> None:
        """
        Slot que se activa cuando el vídeo se reproduce, para mover los marcadores del gráfico.
        """
        if self.fps > 0:
            frame_index = int((position_ms / 1000) * self.fps)
            # Le ordenamos al gráfico que mueva sus marcadores
            self.plot_widget.update_marker_position(frame_index)

    def _update_curve_visibility(self) -> None:
        """Notifica al PlotWidget qué curvas mostrar u ocultar según los checkboxes."""
        for display_name, checkbox in self.checkboxes.items():
            self.plot_widget.set_curve_visibility(display_name, checkbox.isChecked())

    def update_results(self, results: Dict[str, Any]) -> None:
        """Rellena todos los widgets con los nuevos resultados del pipeline."""
        self.clear_results()
        
        self.rep_counter.setText(str(results.get("repeticiones_contadas", "0")))
        self.fps = results.get("fps", 30.0)
        df = results.get("dataframe_metricas")
        
        if df is None or df.empty:
            self.status_label.setText("Estado: No se generaron métricas.")
            return

        self.status_label.setText("Estado: Análisis completado.")
        self.plot_widget.plot_data(df)
        
        curves_found = self.plot_widget._plotted_curves.keys()
        any_cb_visible = False
        for display_name, checkbox in self.checkboxes.items():
            is_visible = display_name in curves_found
            checkbox.setVisible(is_visible)
            checkbox.setChecked(is_visible)
            if is_visible: any_cb_visible = True
        self.visibility_group.setVisible(any_cb_visible)
        
        faults = results.get("fallos_detectados", [])
        if not faults: self.fault_list.addItem("¡No se detectaron fallos!")
        if len(curves_found) == 1 and any_cb_visible:
            self.fault_list.addItem(f"Info: Solo se detectó la '{list(curves_found)[0]}'.")
        for fault in faults:
            self.fault_list.addItem(f"Rep {fault['rep']}: {fault['type']} ({fault['value']})")
        
        # Carga el vídeo y CONECTA la señal de sincronización
        video_path = results.get("debug_video_path")
        if video_path:
            self.video_player.load_video(video_path)
            self.video_player.media_player.positionChanged.connect(self.on_video_position_changed)

    def _create_box(self, title: str, widget: QWidget) -> QFrame:
        """Función helper para crear cajas con título y borde."""
        box = QFrame(); box.setFrameShape(QFrame.StyledPanel); layout = QVBoxLayout(box)
        title_label = QLabel(title); font = title_label.font(); font.setBold(True)
        title_label.setFont(font); title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label); layout.addWidget(widget)
        return box
    
    def clear_results(self) -> None:
        """Limpia todos los resultados y desconecta señales para un nuevo análisis."""
        try:
            self.video_player.media_player.positionChanged.disconnect(self.on_video_position_changed)
        except TypeError:
            pass
        
        self.rep_counter.setText("0"); self.status_label.setText("Listo para analizar")
        self.plot_widget.clear_plots(); self.fault_list.clear()
        self.video_player.clear_media(); self.visibility_group.hide()
