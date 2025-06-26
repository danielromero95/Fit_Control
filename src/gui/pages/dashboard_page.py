from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QCalendarWidget,
    QGroupBox,
    QTextEdit,
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QTextCharFormat, QColor


class DashboardPage(QWidget):
    """Página principal con un calendario y el plan de entrenamiento del día."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.calendar = QCalendarWidget()
        self._highlight_today()
        layout.addWidget(self.calendar)

        self.plan_group = QGroupBox("Plan para Hoy")
        plan_layout = QVBoxLayout(self.plan_group)
        self.plan_text = QTextEdit(readOnly=True)
        self.plan_text.setPlaceholderText(
            "No hay entrenamiento planificado para hoy."
        )
        plan_layout.addWidget(self.plan_text)
        layout.addWidget(self.plan_group)

    def _highlight_today(self) -> None:
        today = QDate.currentDate()
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#3366ff"))
        fmt.setForeground(QColor("white"))
        self.calendar.setDateTextFormat(today, fmt)

    def refresh_dashboard(self) -> None:
        """Actualiza el plan del día utilizando un plan de ejemplo."""

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

        day_names = {
            1: "Lunes",
            2: "Martes",
            3: "Miércoles",
            4: "Jueves",
            5: "Viernes",
            6: "Sábado",
            7: "Domingo",
        }
        today = QDate.currentDate()
        day_es = day_names.get(today.dayOfWeek(), "")

        start_token = f"### {day_es}"
        lines = plan_md.splitlines()
        collecting = False
        extracted: list[str] = []
        for line in lines:
            if collecting:
                if line.startswith("### "):
                    break
                extracted.append(line)
            elif line.startswith(start_token):
                collecting = True
        plan_text = "\n".join(extracted).strip()
        if plan_text:
            self.plan_text.setMarkdown(plan_text)
        else:
            self.plan_text.setMarkdown("Descanso. No hay entrenamiento para hoy.")

