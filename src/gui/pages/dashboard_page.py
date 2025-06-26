from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox
from datetime import datetime

from ... import database


class DashboardPage(QWidget):
    """Página principal que resume el estado de la aplicación."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        self.analysis_card, self.analysis_label = self._create_summary_card(
            "Último Análisis", "No hay análisis guardados."
        )
        self.plan_card, self.plan_label = self._create_summary_card(
            "Plan Activo", "No hay plan activo."
        )

        layout.addWidget(self.analysis_card)
        layout.addWidget(self.plan_card)
        layout.addStretch(1)

    def _create_summary_card(self, title: str, content: str):
        box = QGroupBox(title)
        vbox = QVBoxLayout(box)
        label = QLabel(content)
        label.setWordWrap(True)
        vbox.addWidget(label)
        return box, label

    def refresh_dashboard(self) -> None:
        """Carga los datos más recientes para mostrar en el dashboard."""
        row = database.get_latest_analysis()
        if row:
            try:
                ts = datetime.fromisoformat(row["timestamp"]).strftime("%d %b %Y - %H:%M")
            except Exception:
                ts = row["timestamp"]
            text = f"{row['exercise_name'].title()} - Reps: {row.get('rep_count', 'N/A')} ({ts})"
        else:
            text = "No hay análisis guardados."
        self.analysis_label.setText(text)

        plan_id = database.get_app_state("active_plan_id")
        if plan_id:
            plan = database.get_plan_by_id(int(plan_id))
            if plan:
                try:
                    pt = datetime.fromisoformat(plan["timestamp"]).strftime("%d %b %Y - %H:%M")
                except Exception:
                    pt = plan["timestamp"]
                plan_text = f"{plan['title']} ({pt})"
            else:
                plan_text = "Plan no encontrado."
        else:
            plan_text = "No hay plan activo."
        self.plan_label.setText(plan_text)
