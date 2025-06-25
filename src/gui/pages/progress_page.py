from typing import Dict, Any
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
)
from PyQt5.QtCore import Qt
import pandas as pd
from datetime import datetime
import logging

from ... import database
from ..widgets.results_panel import ResultsPanel


class ProgressPage(QWidget):
    """Página que muestra el historial de análisis guardados."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget, 1)

        self.results_panel = ResultsPanel(self)
        layout.addWidget(self.results_panel, 2)

        self.list_widget.itemClicked.connect(self.on_analysis_selected)

        self.refresh_analysis_list()

    def clear_results(self) -> None:
        self.results_panel.clear_results()

    def update_results(self, results: Dict[str, Any]) -> None:
        self.results_panel.update_results(results)

    def set_theme(self, is_dark: bool) -> None:
        self.results_panel.plot_widget.set_theme(is_dark)

    def refresh_analysis_list(self) -> None:
        """Carga de la base de datos la lista de análisis."""
        self.list_widget.clear()
        for row in database.get_all_analysis_results():
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
        else:
            self.list_widget.setCurrentRow(0)
            first_item = self.list_widget.item(0)
            if first_item:
                self.on_analysis_selected(first_item)

    def on_analysis_selected(self, item: QListWidgetItem) -> None:
        analysis_id = item.data(Qt.UserRole)
        row = database.get_analysis_by_id(int(analysis_id))
        if not row:
            return
        metrics_json = row.get("metrics_df_json")
        df = None
        if metrics_json:
            try:
                df = pd.read_json(metrics_json, orient="split")
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
