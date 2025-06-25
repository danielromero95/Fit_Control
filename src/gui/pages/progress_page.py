from typing import Dict, Any
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from ..widgets.results_panel import ResultsPanel


class ProgressPage(QWidget):
    """Página que muestra los resultados del análisis."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.results_panel = ResultsPanel(self)
        layout.addWidget(self.results_panel)

    def clear_results(self) -> None:
        self.results_panel.clear_results()

    def update_results(self, results: Dict[str, Any]) -> None:
        self.results_panel.update_results(results)

    def set_theme(self, is_dark: bool) -> None:
        self.results_panel.plot_widget.set_theme(is_dark)

