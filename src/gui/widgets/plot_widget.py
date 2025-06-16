# src/gui/widgets/plot_widget.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import pandas as pd
import logging

from src.gui.gui_utils import get_first_available_series

logger = logging.getLogger(__name__)

class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plot_item = pg.PlotWidget()
        self.plot_item.setBackground('w')
        self.plot_item.showGrid(x=True, y=True)
        self.plot_item.setLabel('left', 'Ángulo', units='°')
        self.plot_item.setLabel('bottom', 'Frame')
        
        layout = QVBoxLayout()
        layout.addWidget(self.plot_item)
        self.setLayout(layout)

    def plot_data(self, df_metrics: pd.DataFrame):
        """
        Dibuja las métricas disponibles en el DataFrame.
        """
        self.clear_plots()

        # Intentamos obtener los datos para el eje X y el eje Y
        x_series = get_first_available_series(df_metrics, 'frame_index')
        y_series = get_first_available_series(df_metrics, 'knee_angle')

        if x_series is not None and y_series is not None:
            # Filtramos nulos para que el gráfico no tenga cortes
            valid_data = pd.concat([x_series, y_series], axis=1).dropna()
            
            pen = pg.mkPen(color=(0, 120, 215), width=2)
            self.plot_item.plot(valid_data[x_series.name], valid_data[y_series.name], pen=pen)
            self.plot_item.setTitle("Ángulo de la Rodilla", color="k", size="12pt")
            logger.info(f"Gráfico actualizado con la columna '{y_series.name}'.")
        else:
            self.plot_item.setTitle("Datos de ángulo no disponibles", color="r", size="12pt")
            logger.warning("No se encontraron columnas de ángulo o de frame para dibujar.")

    def clear_plots(self):
        self.plot_item.clear()