from __future__ import annotations

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
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie

from ..widgets.daily_plan_card import DailyPlanCard
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

        self.worker = None
        self.generate_btn.clicked.connect(self.on_generate_plan_clicked)

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


# ---------------------------------------------------------------------------
class PlansPage(QWidget):
    """Página que muestra el plan de entrenamiento activo."""

    def __init__(self, translator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.translator = translator

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        plan_dict = self._load_active_plan_dict()

        title = QLabel(f"Plan Activo: {plan_dict['plan_name']}")
        title.setObjectName("planTitle")
        layout.addWidget(title)

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
            self.scroll_layout.addWidget(card)

        self.scroll_layout.addStretch(1)

        self.new_plan_btn = QPushButton("Generar Nuevo Plan")
        self.new_plan_btn.setObjectName("PrimaryCTAButton")
        self.new_plan_btn.clicked.connect(self._open_generator_dialog)
        layout.addWidget(self.new_plan_btn)

    # --------------------------------------------------
    def _open_generator_dialog(self) -> None:
        dlg = PlanGeneratorDialog(self.translator, self)
        dlg.exec_()

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
