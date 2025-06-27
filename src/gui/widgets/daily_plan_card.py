from __future__ import annotations
from typing import Iterable
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QProgressBar,
    QGraphicsOpacityEffect,
    QPushButton,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPalette
import qtawesome as qta

# Colores centralizados para los iconos
ICON_COLORS = {"dark": "#A0AEC0", "light": "#4A5568"}


class ExerciseRowWidget(QWidget):
    """Fila individual para un ejercicio en la tarjeta del plan."""

    checked = pyqtSignal(bool)
    clicked = pyqtSignal(str)

    def __init__(self, name: str, detail: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.exercise_name = name

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.check_box = QCheckBox()
        self.check_box.stateChanged.connect(self._on_checked)
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

    def _on_checked(self, state: int) -> None:
        checked = state == Qt.Checked
        self.check_lbl.setVisible(checked)
        self.opacity_effect.setOpacity(0.4 if checked else 1.0)
        self.checked.emit(checked)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.exercise_name)
        return super().mousePressEvent(event)


class DailyPlanCard(QWidget):
    """Tarjeta visual robusta para un plan diario, con gestión de tema autónoma."""

    exercise_clicked = pyqtSignal(str)
    start_clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("DailyPlanCard")
        self.setProperty("isRestDay", False)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(6)

        header_layout = QHBoxLayout()
        self.title_lbl = QLabel("...")
        self.title_lbl.setObjectName("planTitle")
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch(1)

        summary_layout = QHBoxLayout()
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(4)
        self.count_icon_lbl = QLabel()
        self.count_lbl = QLabel()
        self.count_lbl.setObjectName("planInfo")
        summary_layout.addWidget(self.count_icon_lbl)
        summary_layout.addWidget(self.count_lbl)
        self.time_icon_lbl = QLabel()
        self.time_lbl = QLabel()
        self.time_lbl.setObjectName("planInfo")
        summary_layout.addWidget(self.time_icon_lbl)
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

        self.rest_label = QLabel("Descanso. No hay entrenamiento para hoy.")
        main_layout.addWidget(self.rest_label)

        self.start_btn = QPushButton("Empezar Entrenamiento")
        self.start_btn.setObjectName("startTrainingButton")
        self.start_btn.clicked.connect(self.start_clicked)
        main_layout.addWidget(self.start_btn)

        self._total_exercises = 0
        self._completed = 0

    def changeEvent(self, event) -> None:
        """Se dispara cuando el estilo cambia, asegurando que los iconos se actualicen."""
        super().changeEvent(event)
        if event.type() == event.Type.StyleChange:
            self._update_theme_dependent_styles()

    def _update_theme_dependent_styles(self) -> None:
        """Actualiza los iconos basándose en el color de fondo de la tarjeta."""
        bg_color = self.palette().color(QPalette.Window)
        is_dark_bg = (
            0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue()
        ) < 128
        icon_color = ICON_COLORS["dark"] if is_dark_bg else ICON_COLORS["light"]
        self.count_icon_lbl.setPixmap(qta.icon("fa5s.dumbbell", color=icon_color).pixmap(14, 14))
        self.time_icon_lbl.setPixmap(qta.icon("fa5s.clock", color=icon_color).pixmap(14, 14))

    def update_plan(self, exercises: Iterable[tuple[str, str]]) -> None:
        """Rellena la tarjeta con los datos de un día de entrenamiento."""
        while item := self.exercises_layout.takeAt(0):
            if widget := item.widget():
                widget.deleteLater()

        exercises_list = list(exercises)
        has_exercises = bool(exercises_list)

        self.start_btn.setVisible(has_exercises)
        self.rest_label.setVisible(not has_exercises)
        self.setProperty("isRestDay", not has_exercises)

        if not has_exercises:
            self.count_lbl.setText("")
            self.time_lbl.setText("")
            self.progress_bar.setValue(0)
            self.start_btn.setEnabled(False)
        else:
            self.count_lbl.setText(f"{len(exercises_list)} ejercicios")
            estimated = 5 + 5 * len(exercises_list)
            self.time_lbl.setText(f"~{estimated} min")
            self._total_exercises = len(exercises_list)
            self._completed = 0
            self.progress_bar.setValue(0)
            for name, detail in exercises_list:
                row = ExerciseRowWidget(name, detail)
                row.checked.connect(self._on_row_checked)
                row.clicked.connect(self.exercise_clicked)
                self.exercises_layout.addWidget(row)
            self.start_btn.setEnabled(True)

        self.style().unpolish(self)
        self.style().polish(self)
        self._update_theme_dependent_styles()

    def _on_row_checked(self, checked: bool) -> None:
        if checked:
            self._completed += 1
        else:
            self._completed = max(0, self._completed - 1)
        if self._total_exercises:
            percent = int(100 * self._completed / self._total_exercises)
            self.progress_bar.setValue(percent)
