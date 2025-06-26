from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout
from datetime import datetime

from ..widgets.dashboard_card import DashboardCard
import pyqtgraph as pg

from ... import database


class DashboardPage(QWidget):
    """Página principal que resume el estado de la aplicación."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QGridLayout(self)
        layout.setSpacing(10)
        self.grid_layout = layout

        # KPI Cards
        self.kpi1_card = DashboardCard("Último Análisis")
        self.kpi1_value = QLabel("N/A")
        self.kpi1_value.setObjectName("kpiValue")
        self.kpi1_sub = QLabel("")
        self.kpi1_sub.setObjectName("kpiSubtitle")
        kpi1_layout = QVBoxLayout(); kpi1_layout.addWidget(self.kpi1_value); kpi1_layout.addWidget(self.kpi1_sub)
        kpi1_widget = QWidget(); kpi1_widget.setLayout(kpi1_layout)
        self.kpi1_card.setContent(kpi1_widget)

        self.kpi2_card = DashboardCard("Métrica Clave")
        self.kpi2_value = QLabel("N/A")
        self.kpi2_value.setObjectName("kpiValue")
        self.kpi2_sub = QLabel("")
        self.kpi2_sub.setObjectName("kpiSubtitle")
        kpi2_layout = QVBoxLayout(); kpi2_layout.addWidget(self.kpi2_value); kpi2_layout.addWidget(self.kpi2_sub)
        kpi2_widget = QWidget(); kpi2_widget.setLayout(kpi2_layout)
        self.kpi2_card.setContent(kpi2_widget)

        self.kpi3_card = DashboardCard("Plan Activo")
        self.kpi3_value = QLabel("N/A")
        self.kpi3_value.setObjectName("kpiValue")
        self.kpi3_sub = QLabel("")
        self.kpi3_sub.setObjectName("kpiSubtitle")
        kpi3_layout = QVBoxLayout(); kpi3_layout.addWidget(self.kpi3_value); kpi3_layout.addWidget(self.kpi3_sub)
        kpi3_widget = QWidget(); kpi3_widget.setLayout(kpi3_layout)
        self.kpi3_card.setContent(kpi3_widget)

        self.kpi4_card = DashboardCard("Sesiones Totales")
        self.kpi4_value = QLabel("0")
        self.kpi4_value.setObjectName("kpiValue")
        self.kpi4_sub = QLabel("")
        self.kpi4_sub.setObjectName("kpiSubtitle")
        kpi4_layout = QVBoxLayout(); kpi4_layout.addWidget(self.kpi4_value); kpi4_layout.addWidget(self.kpi4_sub)
        kpi4_widget = QWidget(); kpi4_widget.setLayout(kpi4_layout)
        self.kpi4_card.setContent(kpi4_widget)

        layout.addWidget(self.kpi1_card, 0, 0)
        layout.addWidget(self.kpi2_card, 0, 1)
        layout.addWidget(self.kpi3_card, 0, 2)
        layout.addWidget(self.kpi4_card, 0, 3)

        # Chart Card
        self.chart_card = DashboardCard("Progreso")
        self.plot_widget = pg.PlotWidget()
        self.chart_card.setContent(self.plot_widget)
        layout.addWidget(self.chart_card, 1, 0, 1, 4)


    def refresh_dashboard(self) -> None:
        """Carga los datos más recientes para mostrar en el dashboard."""
        row = database.get_latest_analysis()
        if row:
            try:
                ts = datetime.fromisoformat(row["timestamp"]).strftime("%d %b %Y - %H:%M")
            except Exception:
                ts = row["timestamp"]
            self.kpi1_value.setText(row["exercise_name"].title())
            self.kpi1_sub.setText(f"Reps: {row.get('rep_count', 'N/A')} ({ts})")
            val = row.get("key_metric_avg")
            self.kpi2_value.setText(f"{val:.2f}" if isinstance(val, (int, float)) else "N/A")
            self.kpi2_sub.setText("Métrica Clave promedio")
        else:
            self.kpi1_value.setText("N/A")
            self.kpi1_sub.setText("No hay análisis guardados.")
            self.kpi2_value.setText("N/A")
            self.kpi2_sub.setText("")

        plan_id = database.get_app_state("active_plan_id")
        if plan_id:
            plan = database.get_plan_by_id(int(plan_id))
            if plan:
                self.kpi3_value.setText(plan["title"])
                try:
                    pt = datetime.fromisoformat(plan["timestamp"]).strftime("%d %b %Y - %H:%M")
                except Exception:
                    pt = plan["timestamp"]
                self.kpi3_sub.setText(pt)
            else:
                self.kpi3_value.setText("N/A")
                self.kpi3_sub.setText("Plan no encontrado")
        else:
            self.kpi3_value.setText("N/A")
            self.kpi3_sub.setText("No hay plan activo")

        total = database.get_total_analysis_count()
        self.kpi4_value.setText(str(total))
        self.kpi4_sub.setText("Análisis guardados")

        exercise_for_chart = row["exercise_name"] if row else None
        if exercise_for_chart:
            rows = database.get_recent_reps_by_exercise(exercise_for_chart)
        else:
            rows = []

        self.plot_widget.clear()
        if rows:
            x = []
            y = []
            for r in rows:
                try:
                    dt = datetime.fromisoformat(r["timestamp"])
                except Exception:
                    continue
                x.append(dt.timestamp())
                y.append(int(r.get("rep_count", 0)))
            pen = pg.mkPen('b', width=2)
            self.plot_widget.plot(x=x, y=y, pen=pen, symbol='o', symbolBrush='b')

