from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
)
from PyQt5.QtCore import QDate, pyqtSignal

from src.gui.widgets.custom_calendar_widget import CustomCalendarWidget
from src.gui.widgets.daily_plan_card import DailyPlanCard
from src import database


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

        self._plan_data = self._load_active_plan()
        self._on_date_selected(QDate.currentDate())

    def refresh_dashboard(self) -> None:
        """Vuelve a cargar el plan activo y refresca la vista."""
        self._plan_data = self._load_active_plan()
        self._on_date_selected(QDate.currentDate())

    def _parse_plan_md(self, plan_md: str) -> dict[str, list[tuple[str, str]]]:
        """Convierte Markdown en un diccionario de plan semanal."""
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

    def _load_active_plan(self) -> dict[str, list[tuple[str, str]]]:
        plan_id = database.get_active_plan_id()
        if plan_id is not None:
            row = database.get_plan_by_id(plan_id)
            if row and row.get("plan_content_md"):
                return self._parse_plan_md(row["plan_content_md"])
        return self._parse_plan_md("")

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
