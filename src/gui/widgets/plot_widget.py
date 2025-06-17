# src/gui/widgets/plot_widget.py
import logging
import pandas as pd
import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import pyqtSignal, Qt, QPointF
from PyQt5.QtGui import QMouseEvent, QGuiApplication
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from typing import Optional, Tuple, List, Dict, Any

from src.gui.gui_utils import get_first_available_series
from src.config import settings

logger = logging.getLogger(__name__)

class PlotWidget(QWidget):
    frame_clicked_signal = pyqtSignal(int)
    CURVE_MAP = {'left_knee_angle': 'Rodilla Izquierda', 'right_knee_angle': 'Rodilla Derecha'}

    def __init__(self, parent=None):
        super().__init__(parent)
        self._x_data: Optional[np.ndarray] = None
        self._is_dark_theme: bool = True
        self._plotted_curves: Dict[str, pg.PlotDataItem] = {}
        self.plot_item = pg.PlotWidget()
        self._vb = self.plot_item.getPlotItem().getViewBox()
        self._vb.setMouseEnabled(x=False, y=False)
        self.v_line = pg.InfiniteLine(angle=90, movable=False)
        self.h_line_low = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen(style=Qt.DotLine))
        self.h_line_high = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen(style=Qt.DotLine))
        self.marker = pg.ScatterPlotItem(size=12, pen=pg.mkPen(None))
        self.h_line_low.setZValue(10); self.h_line_high.setZValue(10)
        self.v_line.setZValue(20); self.marker.setZValue(30)
        self._setup_plot_appearance()
        self._vb.scene().sigMouseClicked.connect(self._on_mouse_event)
        self._vb.scene().sigMouseMoved.connect(self._on_mouse_event)
        self.setFocusPolicy(Qt.StrongFocus)
        layout = QVBoxLayout(); layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.plot_item); self.setLayout(layout)

    def _setup_plot_appearance(self):
        self.plot_item.showGrid(x=True, y=True)
        self.plot_item.setLabel('left', 'Ángulo', units='°'); self.plot_item.setLabel('bottom', 'Frame')
        self.legend = self.plot_item.addLegend(offset=(-30, 30))
        self.plot_item.addItem(self.v_line); self.plot_item.addItem(self.h_line_low)
        self.plot_item.addItem(self.h_line_high); self.plot_item.addItem(self.marker)
        self.set_theme(is_dark=True); self.clear_plots()

    def set_theme(self, is_dark: bool):
        self._is_dark_theme = is_dark
        theme = settings.drawing.dark_theme if is_dark else settings.drawing.light_mode
        plot_params = theme.plot
        self.plot_item.setBackground(plot_params.background_color)
        self.plot_item.getAxis('left').setPen(plot_params.axis_color)
        self.plot_item.getAxis('bottom').setPen(plot_params.axis_color)
        self.v_line.setPen(pg.mkPen(plot_params.vline_color, width=plot_params.vline_thickness, style=Qt.DashLine))
        pen_thresh = pg.mkPen(plot_params.axis_color, width=1, style=Qt.DotLine)
        self.h_line_low.setPen(pen_thresh); self.h_line_high.setPen(pen_thresh)
        self.marker.setBrush(pg.mkBrush(plot_params.vline_color))

    def _on_mouse_event(self, event: Any):
        if not (QGuiApplication.mouseButtons() & Qt.LeftButton): return
        if isinstance(event, QMouseEvent): scene_pos = event.scenePos()
        elif isinstance(event, QPointF): scene_pos = event
        else: return
        if self._x_data is None or len(self._x_data) == 0: return
        if not self._vb.sceneBoundingRect().contains(scene_pos): return
        mouse_point = self._vb.mapSceneToView(scene_pos)
        idx = np.abs(self._x_data - mouse_point.x()).argmin()
        frame_index = self._x_data[idx]
        self.v_line.setPos(frame_index); self.v_line.show()
        main_curve = self._plotted_curves.get('Rodilla Izquierda')
        if main_curve and hasattr(main_curve, 'xData') and len(main_curve.xData) > 0:
            curve_idx = np.searchsorted(main_curve.xData, frame_index, side="left")
            if curve_idx > 0 and (curve_idx == len(main_curve.xData) or abs(frame_index - main_curve.xData[curve_idx-1]) < abs(frame_index - main_curve.xData[curve_idx])):
                curve_idx -=1
            if curve_idx < len(main_curve.yData):
                self.marker.setData([frame_index], [main_curve.yData[curve_idx]])
        self.frame_clicked_signal.emit(frame_index)
        
    def plot_data(self, df_metrics: pd.DataFrame) -> None:
        self.clear_plots()
        try:
            theme = settings.drawing.dark_theme if self._is_dark_theme else settings.drawing.light_mode
            plot_params = theme.plot
            x_series, y_left, y_right = self._get_plot_series(df_metrics)
            if x_series is None: self.plot_item.setTitle("Datos no disponibles", color="r", size="12pt"); return
            self._x_data = x_series.dropna().to_numpy(dtype=int)
            pen_left = pg.mkPen(color=plot_params.line_color_left, width=plot_params.line_thickness)
            pen_right = pg.mkPen(color=plot_params.line_color_right, width=plot_params.line_thickness, style=Qt.DashLine)
            if y_left is not None:
                data = pd.concat([x_series, y_left], axis=1).dropna()
                curve = self.plot_item.plot(data[x_series.name], data[y_left.name], pen=pen_left, name="Rodilla Izquierda", symbol='o', symbolSize=5, symbolBrush=plot_params.line_color_left)
                self._plotted_curves["Rodilla Izquierda"] = curve
            if y_right is not None:
                data = pd.concat([x_series, y_right], axis=1).dropna()
                curve = self.plot_item.plot(data[x_series.name], data[y_right.name], pen=pen_right, name="Rodilla Derecha", symbol='o', symbolSize=5, symbolBrush=plot_params.line_color_right)
                self._plotted_curves["Rodilla Derecha"] = curve
            self.h_line_low.setPos(settings.squat_params.low_thresh); self.h_line_low.show()
            self.h_line_high.setPos(settings.squat_params.high_thresh); self.h_line_high.show()
            self.legend.setVisible(bool(self._plotted_curves))
            self.plot_item.setTitle("Ángulos de Rodilla", color=plot_params.axis_color, size="12pt")
            self.plot_item.autoRange()
        except Exception as e:
            logger.error(f"Error fatal al dibujar los datos: {e}", exc_info=True)

    def set_curve_visibility(self, name: str, visible: bool):
        if name in self._plotted_curves: self._plotted_curves[name].setVisible(visible)

    def clear_plots(self):
        for curve in self._plotted_curves.values(): self.plot_item.removeItem(curve)
        self._plotted_curves.clear(); self._x_data = None
        self.v_line.hide(); self.marker.clear(); self.h_line_low.hide(); self.h_line_high.hide()
        if self.legend: self.legend.setVisible(False)

    def _get_plot_series(self, df_metrics: pd.DataFrame) -> Tuple[Optional[pd.Series], ...]:
        x = get_first_available_series(df_metrics, 'frame_index')
        y_left = get_first_available_series(df_metrics, 'left_knee_angle')
        y_right = get_first_available_series(df_metrics, 'right_knee_angle')
        return x, y_left, y_right