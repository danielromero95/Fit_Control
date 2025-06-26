from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
)
from PyQt5.QtCore import QDate, pyqtSignal

from src.gui.widgets.custom_calendar_widget import CustomCalendarWidget
from src.gui.widgets.daily_plan_card import DailyPlanCard


class DashboardPage(QWidget):
    """Página principal con un calendario y el plan de entrenamiento del día."""

    exercise_selected = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self.calendar = CustomCalendarWidget()
        layout.addWidget(self.calendar)

        self.daily_plan_card = DailyPlanCard()
        layout.addWidget(self.daily_plan_card)
        self.daily_plan_card.exercise_clicked.connect(self.exercise_selected)

        self.calendar.date_selected.connect(self._on_date_selected)

        self._plan_data = self._parse_example_plan()
        self._on_date_selected(QDate.currentDate())

    def refresh_dashboard(self) -> None:
        """Refresca la tarjeta del plan para la fecha seleccionada."""
        self._on_date_selected(QDate.currentDate())

    def _parse_example_plan(self) -> dict[str, list[tuple[str, str]]]:
        """Parsea un plan de ejemplo simple para cada día."""

        plan_md = """
### Lunes
- Sentadillas 3x10
- Press de banca 3x8

### Martes
- Dominadas 4x6
- Curl de bíceps 3x12

### Miércoles
Descanso

### Jueves
- Peso muerto 5x5
- Remo con barra 3x8

### Viernes
- Press militar 4x6
- Fondos en paralelas 3x10

### Sábado
- Cardio ligero 30 minutos

### Domingo
Descanso
"""

        plan: dict[str, list[tuple[str, str]]] = {}
        current_day: str | None = None
        for line in plan_md.splitlines():
            if line.startswith("### "):
                current_day = line[4:].strip()
                plan[current_day] = []
                continue
            if current_day is None or not line.strip():
                continue
            if line.strip().lower().startswith("descanso"):
                plan[current_day] = []
                continue
            if line.startswith("- "):
                text = line[2:].strip()
                parts = text.rsplit(" ", 1)
                if len(parts) == 2:
                    plan[current_day].append((parts[0], parts[1]))
                else:
                    plan[current_day].append((text, ""))
        return plan

    def _on_date_selected(self, date: QDate) -> None:
        day_names = {
            1: "Lunes",
            2: "Martes",
            3: "Miércoles",
            4: "Jueves",
            5: "Viernes",
            6: "Sábado",
            7: "Domingo",
        }
        day_es = day_names.get(date.dayOfWeek(), "")
        exercises = self._plan_data.get(day_es, [])
        self.daily_plan_card.update_plan(exercises)
