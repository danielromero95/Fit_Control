from __future__ import annotations

from datetime import date, timedelta
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QLabel,
    QPushButton,
    QFormLayout,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QTextEdit,
    QStackedWidget,
    QDialog,
    QMessageBox,
    QInputDialog,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMovie

from ..widgets.daily_plan_card import DailyPlanCard
from ..widgets.mini_calendar_widget import MiniCalendarWidget
from ...services.plan_generator import PlanGeneratorWorker
from ... import database


# ---------------------------------------------------------------------------
# Ejemplo de estructura de datos para un plan
sample_plan = {
    "plan_name": "Hipertrofia Clásica - 3 Días",
    "days": [
        {
            "day_name": "Lunes: Tirón (Pull)",
            "exercises": [
                {"name": "Dominadas", "detail": "4x8-12"},
                {"name": "Remo con Barra", "detail": "3x8-10"},
                {"name": "Face Pull", "detail": "3x15-20"},
            ],
        },
        {"day_name": "Martes: Descanso", "exercises": []},
        {
            "day_name": "Miércoles: Empuje (Push)",
            "exercises": [
                {"name": "Press de Banca", "detail": "4x8-12"},
                {"name": "Press Militar con Barra", "detail": "3x8-10"},
                {"name": "Fondos en Paralelas", "detail": "3xAl fallo"},
            ],
        },
        {"day_name": "Jueves: Descanso", "exercises": []},
        {
            "day_name": "Viernes: Piernas",
            "exercises": [
                {"name": "Sentadilla", "detail": "4x8-12"},
                {"name": "Peso Muerto", "detail": "3x6-8"},
                {"name": "Prensa", "detail": "3x10-12"},
            ],
        },
        {"day_name": "Sábado: Descanso", "exercises": []},
        {"day_name": "Domingo: Descanso", "exercises": []},
    ],
}


# ---------------------------------------------------------------------------
class PlanGeneratorDialog(QDialog):
    """Diálogo para generar un nuevo plan de entrenamiento."""

    plan_saved = pyqtSignal()

    def __init__(self, translator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.translator = translator
        self.setWindowTitle(self.translator.tr("generate_plan"))

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.objetivo_cb = QComboBox()
        self.objetivo_cb.addItems(
            [
                "Hipertrofia (Ganar músculo)",
                "Fuerza",
                "Pérdida de Peso",
                "Resistencia",
            ]
        )
        form_layout.addRow(self.translator.tr("main_goal"), self.objetivo_cb)

        self.dias_sb = QSpinBox()
        self.dias_sb.setRange(1, 7)
        self.dias_sb.setValue(3)
        form_layout.addRow("Días por Semana:", self.dias_sb)

        self.nivel_cb = QComboBox()
        self.nivel_cb.addItems(["Principiante", "Intermedio", "Avanzado"])
        form_layout.addRow("Nivel de Experiencia:", self.nivel_cb)

        self.enfoque_le = QLineEdit()
        form_layout.addRow("Grupos Musculares (Opcional):", self.enfoque_le)

        layout.addLayout(form_layout)

        self.generate_btn = QPushButton(self.translator.tr("generate_plan"))
        layout.addWidget(self.generate_btn)

        self.results_stack = QStackedWidget()
        self.results_text_edit = QTextEdit()
        self.results_text_edit.setReadOnly(True)
        self.results_text_edit.setPlaceholderText(
            "Aquí aparecerá tu plan de entrenamiento..."
        )
        self.results_stack.addWidget(self.results_text_edit)

        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_movie = QMovie("assets/Gym_Loading_Gif.gif")
        self.loading_label.setMovie(self.loading_movie)
        self.results_stack.addWidget(self.loading_label)

        layout.addWidget(self.results_stack, 1)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton(self.translator.tr("save_plan"))
        self.save_activate_btn = QPushButton("Guardar y Activar")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.save_activate_btn)
        layout.addLayout(btn_layout)

        self.worker = None
        self.generate_btn.clicked.connect(self.on_generate_plan_clicked)
        self.save_btn.clicked.connect(self._on_save_clicked)
        self.save_activate_btn.clicked.connect(self._on_save_activate_clicked)

    # --------------------------------------------------
    def on_generate_plan_clicked(self) -> None:
        objetivo = self.objetivo_cb.currentText()
        dias = self.dias_sb.value()
        nivel = self.nivel_cb.currentText()
        enfoque = self.enfoque_le.text().strip()

        self.generate_btn.setEnabled(False)
        self.results_stack.setCurrentWidget(self.loading_label)
        self.loading_movie.start()

        self.worker = PlanGeneratorWorker(objetivo, dias, nivel, enfoque)
        self.worker.finished.connect(self.on_plan_generation_finished)
        self.worker.error.connect(self.on_plan_generation_error)
        self.worker.start()

    def on_plan_generation_finished(self, plan_text: str) -> None:
        self.generate_btn.setEnabled(True)
        self.loading_movie.stop()
        self.results_stack.setCurrentWidget(self.results_text_edit)
        self.results_text_edit.setMarkdown(plan_text)

    def on_plan_generation_error(self, error_message: str) -> None:
        self.generate_btn.setEnabled(True)
        self.loading_movie.stop()
        self.results_stack.setCurrentWidget(self.results_text_edit)
        self.results_text_edit.setPlainText("")
        QMessageBox.critical(self, "Error generando plan", error_message)

    # --------------------------------------------------
    def _on_save_clicked(self) -> None:
        self._save_plan(activate=False)

    # --------------------------------------------------
    def _on_save_activate_clicked(self) -> None:
        if self._save_plan(activate=True):
            self.accept()

    # --------------------------------------------------
    def _save_plan(self, activate: bool) -> int | None:
        md = self.results_text_edit.toPlainText().strip()
        if not md:
            QMessageBox.warning(self, "Error", "No hay plan para guardar")
            return None
        title, ok = QInputDialog.getText(self, "Nombre del Plan", "Título:")
        if not ok or not title.strip():
            return None
        plan_id = database.save_training_plan(title.strip(), md)
        if activate:
            database.set_app_state("active_plan_id", str(plan_id))
        self.plan_saved.emit()
        return plan_id


class SwitchPlanDialog(QDialog):
    """Dialogo para elegir otro plan guardado."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Seleccionar Plan")

        layout = QVBoxLayout(self)
        self.plan_cb = QComboBox()
        for row in database.get_all_training_plans():
            self.plan_cb.addItem(row.get("title", ""), row.get("id"))
        layout.addWidget(self.plan_cb)
        btn = QPushButton("Seleccionar")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def selected_plan_id(self) -> int | None:
        return self.plan_cb.currentData()


# ---------------------------------------------------------------------------
class PlansPage(QWidget):
    """Página que muestra el plan de entrenamiento activo."""

    exercise_selected = pyqtSignal(str)

    def __init__(self, translator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.translator = translator

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        plan_dict = self._load_active_plan_dict()

        header_layout = QHBoxLayout()
        self.title_lbl = QLabel(f"Plan Activo: {plan_dict['plan_name']}")
        self.title_lbl.setObjectName("planTitle")
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch(1)
        self.switch_plan_btn = QPushButton("Cambiar Plan")
        self.switch_plan_btn.clicked.connect(self._on_switch_plan)
        header_layout.addWidget(self.switch_plan_btn)
        layout.addLayout(header_layout)

        self.mini_calendar = MiniCalendarWidget()
        layout.addWidget(self.mini_calendar)

        start_week = date.today() - timedelta(days=date.today().weekday())
        workout_dates = [
            start_week + timedelta(days=i)
            for i, day in enumerate(plan_dict["days"])
            if day.get("exercises")
        ]
        self.mini_calendar.set_workout_dates(workout_dates)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area, 1)

        container = QWidget()
        container.setObjectName("planScrollContainer")
        self.scroll_layout = QVBoxLayout(container)
        self.scroll_layout.setSpacing(15)
        self.scroll_area.setWidget(container)

        for day in plan_dict["days"]:
            card = DailyPlanCard()
            card.title_lbl.setText(day["day_name"])
            exercises = [
                (ex["name"], ex["detail"]) for ex in day.get("exercises", [])
            ]
            card.update_plan(exercises)
            card.exercise_clicked.connect(self.exercise_selected)
            self.scroll_layout.addWidget(card)

        self.scroll_layout.addStretch(1)

        self.new_plan_btn = QPushButton("Generar Nuevo Plan")
        self.new_plan_btn.setObjectName("PrimaryCTAButton")
        self.new_plan_btn.clicked.connect(self._open_generator_dialog)
        layout.addWidget(self.new_plan_btn)

    # --------------------------------------------------
    def _open_generator_dialog(self) -> None:
        dlg = PlanGeneratorDialog(self.translator, self)
        dlg.plan_saved.connect(self._refresh_plan)
        dlg.exec_()

    # --------------------------------------------------
    def _on_switch_plan(self) -> None:
        dlg = SwitchPlanDialog(self)
        if dlg.exec_():
            plan_id = dlg.selected_plan_id()
            if plan_id is not None:
                database.set_app_state("active_plan_id", str(plan_id))
                self._refresh_plan()

    # --------------------------------------------------
    def _refresh_plan(self) -> None:
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        plan_dict = self._load_active_plan_dict()
        self.title_lbl.setText(f"Plan Activo: {plan_dict['plan_name']}")
        start_week = date.today() - timedelta(days=date.today().weekday())
        workout_dates = []
        for i, day in enumerate(plan_dict["days"]):
            card = DailyPlanCard()
            card.title_lbl.setText(day["day_name"])
            exercises = [
                (ex["name"], ex["detail"]) for ex in day.get("exercises", [])
            ]
            card.update_plan(exercises)
            card.exercise_clicked.connect(self.exercise_selected)
            self.scroll_layout.addWidget(card)
            if exercises:
                workout_dates.append(start_week + timedelta(days=i))

        self.mini_calendar.set_workout_dates(workout_dates)
        self.scroll_layout.addStretch(1)

    # --------------------------------------------------
    def _parse_plan_md(self, md: str) -> dict:
        plan: dict[str, list[dict[str, str]]] = {"plan_name": "", "days": []}
        current_day: dict | None = None
        for line in md.splitlines():
            if line.startswith("### "):
                current_day = {"day_name": line[4:].strip(), "exercises": []}
                plan["days"].append(current_day)
                continue
            if current_day is None or not line.strip():
                continue
            if line.lower().startswith("descanso"):
                current_day["exercises"] = []
                continue
            if line.startswith("- "):
                text = line[2:].strip()
                parts = text.rsplit(" ", 1)
                if len(parts) == 2:
                    name, detail = parts
                else:
                    name, detail = text, ""
                current_day["exercises"].append({"name": name, "detail": detail})
        return plan

    def _load_active_plan_dict(self) -> dict:
        plan_id = database.get_active_plan_id()
        if plan_id is not None:
            row = database.get_plan_by_id(plan_id)
            if row and row.get("plan_content_md"):
                plan = self._parse_plan_md(row["plan_content_md"])
                plan["plan_name"] = row.get("title", "")
                return plan
        return sample_plan
