from typing import Dict, Any, List
from io import StringIO
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QComboBox,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from pyqtgraph import DateAxisItem
import pandas as pd
from datetime import datetime
import logging

from ... import database
from ..widgets.results_panel import ResultsPanel
from src.config import settings


class ProgressPage(QWidget):
    """Página que muestra el historial de análisis guardados."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._is_dark_theme: bool = True
        self._chart_data: Dict[str, List[float]] = {}

        layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        self.exercise_combo = QComboBox()
        for name in settings.exercises.keys():
            self.exercise_combo.addItem(name)
        top_layout.addWidget(self.exercise_combo)

        self.metric_combo = QComboBox()
        self.metric_combo.addItems(["Repeticiones", "Métrica Clave"])
        top_layout.addWidget(self.metric_combo)

        self.list_widget = QListWidget()
        top_layout.addWidget(self.list_widget, 1)

        layout.addLayout(top_layout)

        self.progress_chart = pg.PlotWidget(axisItems={'bottom': DateAxisItem()})
        self.progress_chart.setLabel('left', 'Valor')
        layout.addWidget(self.progress_chart, 1)

        self.results_panel = ResultsPanel(self)
        layout.addWidget(self.results_panel, 2)

        self.delete_btn = QPushButton("Borrar Análisis Seleccionado")
        layout.addWidget(self.delete_btn)

        self.list_widget.itemClicked.connect(self.on_analysis_selected)
        self.exercise_combo.currentTextChanged.connect(self.refresh_analysis_list)
        self.metric_combo.currentTextChanged.connect(self.update_plot_view)
        self.delete_btn.clicked.connect(self.on_delete_selected)

        self.refresh_analysis_list(self.exercise_combo.currentText())

    def clear_results(self) -> None:
        self.results_panel.clear_results()

    def update_results(self, results: Dict[str, Any]) -> None:
        self.results_panel.update_results(results)

    def set_theme(self, is_dark: bool) -> None:
        self._is_dark_theme = is_dark
        self.results_panel.plot_widget.set_theme(is_dark)
        theme = settings.drawing.dark_theme if is_dark else settings.drawing.light_theme
        plot_params = theme.plot
        self.progress_chart.setBackground(plot_params.background_color)
        axis_pen = pg.mkPen(color=plot_params.axis_color)
        self.progress_chart.getAxis('left').setPen(axis_pen)
        self.progress_chart.getAxis('bottom').setPen(axis_pen)
        self.update_plot_view()

    def refresh_analysis_list(self, exercise_name: str) -> None:
        """Carga de la base de datos la lista de análisis filtrados por ejercicio."""
        self.list_widget.clear()
        rows = database.get_analysis_results_by_exercise(exercise_name)
        for row in rows:
            try:
                ts = datetime.fromisoformat(row["timestamp"])
                formatted = ts.strftime("%d %b %Y - %H:%M")
            except Exception:
                formatted = row["timestamp"]
            item_text = f"{row['exercise_name'].title()} - {formatted}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, row['id'])
            self.list_widget.addItem(item)

        if self.list_widget.count() == 0:
            self.results_panel.show_empty_state()
            self.progress_chart.clear()
            self._chart_data = {}
        else:
            self.list_widget.setCurrentRow(0)
            first_item = self.list_widget.item(0)
            if first_item:
                self.on_analysis_selected(first_item)
            self.plot_progress_chart(rows)
            self.update_plot_view()

    def on_analysis_selected(self, item: QListWidgetItem) -> None:
        analysis_id = item.data(Qt.UserRole)
        row = database.get_analysis_by_id(int(analysis_id))
        if not row:
            return
        metrics_json = row.get("metrics_df_json")
        df = None
        if metrics_json:
            try:
                df = pd.read_json(StringIO(metrics_json), orient="split")
            except ValueError as e:
                logging.error("Error parsing JSON for analysis %s: %s", analysis_id, e)
                self.results_panel.clear_results()
                self.results_panel.status_label.setText("Datos corruptos para este análisis.")
                return
        full_results = {
            "repeticiones_contadas": row.get("rep_count"),
            "debug_video_path": row.get("video_path"),
            "dataframe_metricas": df,
            "exercise": row.get("exercise_name"),
        }
        self.results_panel.update_results(full_results)

    def plot_progress_chart(self, rows: List[Dict[str, Any]]) -> None:
        """Extrae los datos de las filas y los almacena para el gráfico."""
        self._chart_data = {"timestamps": [], "rep_count": [], "key_metric": []}

        for row in rows:
            try:
                dt = datetime.fromisoformat(row["timestamp"])
            except Exception:
                continue
            self._chart_data["timestamps"].append(dt.timestamp())
            self._chart_data["rep_count"].append(int(row.get("rep_count", 0)))
            metric_val = row.get("key_metric_avg")
            if metric_val is not None:
                try:
                    self._chart_data["key_metric"].append(float(metric_val))
                except ValueError:
                    self._chart_data["key_metric"].append(None)

        self.update_plot_view()

    def update_plot_view(self) -> None:
        """Redibuja el gráfico en función de la métrica seleccionada."""
        self.progress_chart.clear()
        if not self._chart_data.get("timestamps"):
            return

        theme = settings.drawing.dark_theme if self._is_dark_theme else settings.drawing.light_theme
        plot_params = theme.plot
        line_color = plot_params.line_color_left
        pen = pg.mkPen(color=line_color, width=plot_params.line_thickness)

        metric = self.metric_combo.currentText()
        y_data = []
        if metric == "Repeticiones":
            y_data = self._chart_data.get("rep_count", [])
            self.progress_chart.setLabel('left', 'Repeticiones')
        else:
            y_data = self._chart_data.get("key_metric", [])
            self.progress_chart.setLabel('left', 'Métrica Clave')

        if not y_data:
            return

        self.progress_chart.setTitle(
            f"Evolución de Repeticiones para {self.exercise_combo.currentText().title()}"
        )
        self.progress_chart.plot(
            x=self._chart_data["timestamps"],
            y=y_data,
            pen=pen,
            symbol='o',
            symbolBrush=line_color,
        )

    def on_delete_selected(self) -> None:
        item = self.list_widget.currentItem()
        if not item:
            return
        analysis_id = item.data(Qt.UserRole)
        reply = QMessageBox.question(
            self,
            "Confirmar Borrado",
            "¿Seguro que deseas borrar este análisis?",
        )
        if reply == QMessageBox.Yes:
            database.delete_analysis_by_id(int(analysis_id))
            self.refresh_analysis_list(self.exercise_combo.currentText())
