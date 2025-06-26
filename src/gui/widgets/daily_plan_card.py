from __future__ import annotations

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from typing import Iterable
import qtawesome as qta

class ExerciseRowWidget(QWidget):
    """Fila individual de ejercicio en el plan diario."""

    def __init__(self, name: str, detail: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
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

class DailyPlanCard(QWidget):
    """Tarjeta que muestra el plan diario de entrenamiento."""

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
        self.subtitle_lbl = QLabel("")
        self.subtitle_lbl.setObjectName("planSubtitle")
        header_layout.addWidget(self.subtitle_lbl)
        main_layout.addLayout(header_layout)

        self.exercises_layout = QVBoxLayout()
        self.exercises_layout.setSpacing(8)
        main_layout.addLayout(self.exercises_layout)

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
            self.subtitle_lbl.setText("")
            return

        self.subtitle_lbl.setText(f"{len(exercises_list)} ejercicios")
        for name, detail in exercises_list:
            row = ExerciseRowWidget(name, detail)
            self.exercises_layout.addWidget(row)

