# src/gui/widgets/plot_widget.py

import logging
import pandas as pd
import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import pyqtSignal, Qt, QPointF
from PyQt5.QtGui import QGuiApplication, QMouseEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from typing import Optional, Tuple, List, Dict, Any

from src.gui.gui_utils import get_first_available_series
from src.config import settings

logger = logging.getLogger(__name__)

class PlotWidget(QWidget):
    """
    Widget de gráficos interactivo y tematizable. Implementa "clic y arrastre"
    para explorar los resultados, con feedback visual y tooltips automáticos.
    """
    frame_clicked_signal = pyqtSignal(int)
    
    # Mapeo centralizado de nombres de columna a nombres para mostrar en la GUI.
    CURVE_MAP = {
        'left_knee_angle': 'Rodilla Izquierda',
        'right_knee_angle': 'Rodilla Derecha'
    }

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Inicializa el widget del gráfico y todos sus componentes visuales."""
        super().__init__(parent)
        self._x_data: Optional[np.ndarray] = None
        self._is_dark_theme: bool = True
        self._plotted_curves: Dict[str, pg.PlotDataItem] = {}
        
        self.plot_item = pg.PlotWidget()
        self._vb = self.plot_item.getPlotItem().getViewBox()
        
        # Desactivamos el comportamiento por defecto del ratón para controlarlo nosotros.
        self._vb.setMouseEnabled(x=False, y=False)
        self._vb.wheelEvent = lambda ev: None # Desactiva el zoom con la rueda
        
        # --- Creación de Elementos de Feedback Visual ---
        self.v_line = pg.InfiniteLine(angle=90, movable=False)
        self.h_line_low = pg.InfiniteLine(angle=0, movable=False)
        self.h_line_high = pg.InfiniteLine(angle=0, movable=False)
        self.marker = pg.ScatterPlotItem(size=12, pen=pg.mkPen(None))
        
        # Aseguramos que los elementos de feedback se dibujen en el orden correcto.
        self.h_line_low.setZValue(10)
        self.h_line_high.setZValue(10)
        self.v_line.setZValue(20)
        self.marker.setZValue(30)
        
        self._setup_plot_appearance()
        
        # Conectamos las señales de ratón al manejador unificado.
        self._vb.scene().sigMouseClicked.connect(self._on_mouse_event)
        self._vb.scene().sigMouseMoved.connect(self._on_mouse_event)
        
        self.setFocusPolicy(Qt.StrongFocus)
        layout = QVBoxLayout(); layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.plot_item)
        self.setLayout(layout)

    def _setup_plot_appearance(self) -> None:
        """Configura la apariencia estática del gráfico (ejes, leyenda, etc.)."""
        self.plot_item.showGrid(x=True, y=True)
        self.plot_item.setLabel('left', 'Ángulo', units='°')
        self.plot_item.setLabel('bottom', 'Frame')
        self.legend = self.plot_item.addLegend()
        
        # --- Anclamos la leyenda abajo a la derecha ---
        # El primer (1,1) se refiere a la esquina inferior derecha de la leyenda.
        # El segundo (1,1) se refiere a la esquina inferior derecha del gráfico.
        self.legend.anchor(itemPos=(1, 1), parentPos=(1, 1))

        for item in [self.v_line, self.h_line_low, self.h_line_high, self.marker]:
            self.plot_item.addItem(item)
        
        self.set_theme(is_dark=True)
        self.clear_plots()

    def set_theme(self, is_dark: bool) -> None:
        """Actualiza los colores del gráfico según el tema (claro/oscuro)."""
        self._is_dark_theme = is_dark
        theme = settings.drawing.dark_theme if is_dark else settings.drawing.light_theme
        plot_params = theme.plot
        
        self.plot_item.setBackground(plot_params.background_color)
        axis_pen = pg.mkPen(color=plot_params.axis_color)
        self.plot_item.getAxis('left').setPen(axis_pen)
        self.plot_item.getAxis('bottom').setPen(axis_pen)
        
        self.v_line.setPen(pg.mkPen(plot_params.vline_color, width=plot_params.vline_thickness, style=Qt.DashLine))
        thresh_pen = pg.mkPen(color=plot_params.threshold_color, width=1, style=Qt.DotLine)
        self.h_line_low.setPen(thresh_pen)
        self.h_line_high.setPen(thresh_pen)
        self.marker.setBrush(pg.mkBrush(plot_params.vline_color))

    def _on_mouse_event(self, event: Any) -> None:
        """Manejador unificado y robusto para eventos de clic y arrastre del ratón."""
        if not (QGuiApplication.mouseButtons() & Qt.LeftButton):
            return

        # Normalizamos el evento para obtener la posición, sea de clic o de movimiento
        scene_pos = event if isinstance(event, QPointF) else event.scenePos()
        
        if self._x_data is None or len(self._x_data) == 0: return
        if not self._vb.sceneBoundingRect().contains(scene_pos): return
            
        mouse_point = self._vb.mapSceneToView(scene_pos)
        idx = np.abs(self._x_data - mouse_point.x()).argmin()
        frame_index = self._x_data[idx]
        
        self.update_marker_position(frame_index)
        self.frame_clicked_signal.emit(frame_index)
        
    def update_marker_position(self, frame_index: int) -> None:
        """Mueve los elementos de feedback visual a un frame específico."""
        if self._x_data is None: return

        self.v_line.setPos(frame_index)
        self.v_line.show()

        # Posiciona el marcador en la curva principal (izquierda)
        main_curve_display_name = self.CURVE_MAP.get('left_knee_angle')
        main_curve = self._plotted_curves.get(main_curve_display_name)
        if main_curve and hasattr(main_curve, 'xData') and len(main_curve.xData) > 0:
            curve_idx = np.searchsorted(main_curve.xData, frame_index, side="left")
            if 0 < curve_idx < len(main_curve.xData) and abs(frame_index - main_curve.xData[curve_idx-1]) < abs(frame_index - main_curve.xData[curve_idx]):
                curve_idx -= 1
            if curve_idx < len(main_curve.yData):
                self.marker.setData([frame_index], [main_curve.yData[curve_idx]])

    def plot_data(self, df_metrics: pd.DataFrame) -> None:
        """Dibuja las métricas desde el DataFrame y activa los elementos visuales."""
        # 1) Limpiamos todo lo anterior
        self.clear_plots()
        try:
            # 2) Seleccionamos el tema
            theme = settings.drawing.dark_theme if self._is_dark_theme else settings.drawing.light_theme
            plot_params = theme.plot
            # 3) Extraemos la serie de frames
            x_series, _, _ = self._get_plot_series(df_metrics) # Solo necesitamos la serie X aquí

            if x_series is None:
                self.plot_item.setTitle("Datos no disponibles", color="r", size="12pt")
                return
            
            self._x_data = x_series.dropna().to_numpy(dtype=int)

            # 4) Iteramos sobre cada curva de nuestro mapa
            for logical_name, display_name in self.CURVE_MAP.items():
                y_series = get_first_available_series(df_metrics, logical_name)
                if y_series is not None:
                    data = pd.concat([x_series, y_series], axis=1).dropna()
                    if not data.empty:
                        self._add_curve_to_plot(data, x_series.name, y_series.name, logical_name, display_name)
            
            # Muestra las líneas de umbral si hay curvas dibujadas
            if self._plotted_curves:
                self.h_line_low.setPos(settings.squat_params.low_thresh)
                self.h_line_low.show()
                self.h_line_high.setPos(settings.squat_params.high_thresh)
                self.h_line_high.show()
            
            self.legend.setVisible(bool(self._plotted_curves))
            self.plot_item.setTitle("Ángulos de Rodilla", color=plot_params.axis_color, size="12pt")
            self.plot_item.autoRange()
        except Exception as e:
            logger.error(f"Error fatal al dibujar los datos del gráfico: {e}", exc_info=True)

    def _add_curve_to_plot(self, data, x_name, y_name, logical_name, display_name):
        """Helper para añadir una curva al gráfico y a la leyenda."""
        theme = settings.drawing.dark_theme if self._is_dark_theme else settings.drawing.light_theme
        plot_params = theme.plot
        is_right_curve = 'right' in logical_name
        pen_color = plot_params.line_color_right if is_right_curve else plot_params.line_color_left
        pen_style = Qt.DashLine if is_right_curve else Qt.SolidLine
        pen = pg.mkPen(color=pen_color, width=plot_params.line_thickness, style=pen_style)
        
        curve = self.plot_item.plot(data[x_name], data[y_name], pen=pen, name=display_name,
                                    symbol='o', symbolSize=5, symbolBrush=pen_color)
        self._plotted_curves[display_name] = curve
        
    def set_curve_visibility(self, name: str, visible: bool):
        """Muestra u oculta una curva y actualiza la leyenda."""
        if name not in self._plotted_curves: return
        
        self._plotted_curves[name].setVisible(visible)
        
        # Reconstruimos la leyenda para que solo muestre los items visibles
        self.legend.clear()
        for display_name, curve in self._plotted_curves.items():
            if curve.isVisible():
                self.legend.addItem(curve, display_name)
        self.legend.setVisible(any(c.isVisible() for c in self._plotted_curves.values()))

    def clear_plots(self):
        """Limpia solo los elementos dinámicos (curvas, marcadores, etc.)."""
        for curve in self._plotted_curves.values():
            self.plot_item.removeItem(curve)
        self._plotted_curves.clear()
        self._x_data = None
        self.v_line.hide(); self.marker.clear()
        self.h_line_low.hide(); self.h_line_high.hide()
        if self.legend: self.legend.setVisible(False)

    def _get_plot_series(self, df_metrics: pd.DataFrame) -> Tuple[Optional[pd.Series], ...]:
        """Helper para extraer las series de datos a dibujar."""
        x = get_first_available_series(df_metrics, 'frame_index')
        y_left = get_first_available_series(df_metrics, 'left_knee_angle')
        y_right = get_first_available_series(df_metrics, 'right_knee_angle')
        return x, y_left, y_right