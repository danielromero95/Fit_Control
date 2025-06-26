from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QProgressBar,
    QGraphicsOpacityEffect,
)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import Iterable
import qtawesome as qta

class ExerciseRowWidget(QWidget):
    """Fila individual de ejercicio en el plan diario."""

    checked = pyqtSignal(bool)
    clicked = pyqtSignal(str)

    def __init__(self, name: str, detail: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.exercise_name = name

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.check_box = QCheckBox()
        self.check_box.stateChanged.connect(self.on_checked)
        layout.addWidget(self.check_box)

        self.check_lbl = QLabel()
        self.check_lbl.setPixmap(qta.icon("fa5s.check-circle").pixmap(16, 16))
        self.check_lbl.hide()
        layout.addWidget(self.check_lbl)

        self.name_lbl = QLabel(name)
        self.name_lbl.setObjectName("exerciseName")
        layout.addWidget(self.name_lbl)
        layout.addStretch(1)
        self.detail_lbl = QLabel(detail)
        self.detail_lbl.setObjectName("exerciseDetail")
        layout.addWidget(self.detail_lbl)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

    # --------------------------------------------------
    def on_checked(self, state: int) -> None:
        checked = state == Qt.Checked
        self.check_lbl.setVisible(checked)
        self.opacity_effect.setOpacity(0.4 if checked else 1.0)
        self.checked.emit(checked)

    def mousePressEvent(self, event):  # pragma: no cover - UI interaction
        self.clicked.emit(self.exercise_name)
        return super().mousePressEvent(event)


class DailyPlanCard(QWidget):
    """Tarjeta que muestra el plan diario de entrenamiento."""

    exercise_clicked = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("DailyPlanCard")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(6)

        header_layout = QHBoxLayout()
        self.title_lbl = QLabel("Plan para Hoy")
        self.title_lbl.setObjectName("planTitle")
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch(1)

        summary_layout = QHBoxLayout()
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(4)
        self.count_icon_lbl = QLabel()
        self.count_icon_lbl.setPixmap(qta.icon("fa5s.dumbbell").pixmap(14, 14))
        summary_layout.addWidget(self.count_icon_lbl)
        self.count_lbl = QLabel("")
        self.count_lbl.setObjectName("planSubtitle")
        summary_layout.addWidget(self.count_lbl)
        self.time_icon_lbl = QLabel()
        self.time_icon_lbl.setPixmap(qta.icon("fa5s.clock").pixmap(14, 14))
        summary_layout.addWidget(self.time_icon_lbl)
        self.time_lbl = QLabel("")
        self.time_lbl.setObjectName("planSubtitle")
        summary_layout.addWidget(self.time_lbl)
        header_layout.addLayout(summary_layout)

        main_layout.addLayout(header_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("dayProgress")
        self.progress_bar.setMaximumHeight(6)
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.exercises_layout = QVBoxLayout()
        self.exercises_layout.setSpacing(8)
        main_layout.addLayout(self.exercises_layout)

        self._total_exercises = 0
        self._completed = 0

    # --------------------------------------------------------------
    def update_plan(self, exercises: Iterable[tuple[str, str]]) -> None:
        """Actualiza la lista de ejercicios mostrados."""
        while self.exercises_layout.count():
            item = self.exercises_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        exercises_list = list(exercises)
        if not exercises_list:
            lbl = QLabel("Descanso. No hay entrenamiento para hoy.")
            self.exercises_layout.addWidget(lbl)
            self.count_lbl.setText("")
            self.time_lbl.setText("")
            self.progress_bar.setValue(0)
            return

        self.count_lbl.setText(f"{len(exercises_list)} ejercicios")
        # Duración estimada simple: 5 min calentamiento + 5 min por ejercicio
        estimated = 5 + 5 * len(exercises_list)
        self.time_lbl.setText(f"{estimated} min")
        self._total_exercises = len(exercises_list)
        self._completed = 0
        self.progress_bar.setValue(0)

        for name, detail in exercises_list:
            row = ExerciseRowWidget(name, detail)
            row.checked.connect(self._on_row_checked)
            row.clicked.connect(self.exercise_clicked)
            self.exercises_layout.addWidget(row)

    def _on_row_checked(self, checked: bool) -> None:
        if checked:
            self._completed += 1
        else:
            self._completed = max(0, self._completed - 1)
        if self._total_exercises:
            percent = int(100 * self._completed / self._total_exercises)
            self.progress_bar.setValue(percent)

