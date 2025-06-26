from datetime import datetime
import os

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QTextEdit,
    QLabel,
    QFormLayout,
    QSpinBox,
    QDoubleSpinBox,
    QLineEdit,
    QPushButton,
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import pyqtgraph as pg

from ... import database
from .analysis_page import AnalysisPage


class ExerciseDetailPage(QWidget):
    """Detalle de un ejercicio con varias pestañas."""

    def __init__(
        self,
        on_video_selected,
        on_rotation_requested,
        on_open_file_dialog,
        on_start_analysis,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Tab Descripción
        desc_widget = QWidget()
        desc_layout = QVBoxLayout(desc_widget)
        self.description_edit = QTextEdit()
        self.description_edit.setReadOnly(True)
        desc_layout.addWidget(self.description_edit)
        self.tabs.addTab(desc_widget, "Ejercicio")

        # Tab Músculos
        muscles_widget = QWidget()
        muscles_layout = QVBoxLayout(muscles_widget)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        muscles_layout.addWidget(self.image_label)
        self.tabs.addTab(muscles_widget, "Músculos")

        # Tab Estadísticas
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        form = QFormLayout()
        self.reps_spin = QSpinBox()
        self.reps_spin.setRange(0, 1000)
        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0, 1000)
        self.weight_spin.setDecimals(2)
        self.notes_edit = QLineEdit()
        self.save_log_btn = QPushButton("Guardar")
        form.addRow("Reps", self.reps_spin)
        form.addRow("Peso", self.weight_spin)
        form.addRow("Notas", self.notes_edit)
        form.addRow(self.save_log_btn)
        stats_layout.addLayout(form)
        self.progress_plot = pg.PlotWidget()
        stats_layout.addWidget(self.progress_plot, 1)
        self.tabs.addTab(stats_widget, "Estadísticas")

        # Tab Análisis de Técnica
        analysis_container = QWidget()
        analysis_layout = QVBoxLayout(analysis_container)
        self.analysis_page = AnalysisPage(
            on_video_selected,
            on_rotation_requested,
            on_open_file_dialog,
            on_start_analysis,
        )
        analysis_layout.addWidget(self.analysis_page)
        self.tabs.addTab(analysis_container, "Análisis de Técnica")

        self.exercise_id: int | None = None
        self.save_log_btn.clicked.connect(self.on_save_log)

    def load_exercise(self, exercise_id: int) -> None:
        """Carga la información del ejercicio y actualiza las pestañas."""
        self.exercise_id = exercise_id
        row = database.get_exercise_by_id(exercise_id)
        if not row:
            return
        self.description_edit.setMarkdown(row.get("description_md", ""))
        img_path = row.get("icon_path")
        if img_path and os.path.exists(img_path):
            self.image_label.setPixmap(QPixmap(img_path))
        else:
            self.image_label.clear()
        self._refresh_logs()

    def on_save_log(self) -> None:
        if self.exercise_id is None:
            return
        timestamp = datetime.utcnow().isoformat()
        reps = int(self.reps_spin.value())
        weight = float(self.weight_spin.value())
        notes = self.notes_edit.text().strip() or None
        database.add_manual_log(timestamp, self.exercise_id, reps, weight, notes)
        self.reps_spin.setValue(0)
        self.weight_spin.setValue(0)
        self.notes_edit.clear()
        self._refresh_logs()

    def _refresh_logs(self) -> None:
        if self.exercise_id is None:
            return
        rows = database.get_logs_for_exercise(self.exercise_id)
        self.progress_plot.clear()
        if not rows:
            return
        x = []
        y = []
        for r in rows:
            try:
                dt = datetime.fromisoformat(r["timestamp"])
            except Exception:
                continue
            x.append(dt.timestamp())
            y.append(float(r.get("weight", 0)))
        pen = pg.mkPen('b', width=2)
        self.progress_plot.plot(x=x, y=y, pen=pen, symbol='o', symbolBrush='b')

