from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QTextEdit,
    QPushButton,
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

from ...services.plan_generator import PlanGeneratorWorker


class PlansPage(QWidget):
    """Página para generar planes de entrenamiento personalizados."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        main_layout = QVBoxLayout(self)

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
        form_layout.addRow("Objetivo Principal:", self.objetivo_cb)

        self.dias_sb = QSpinBox()
        self.dias_sb.setRange(1, 7)
        self.dias_sb.setValue(3)
        form_layout.addRow("Días por Semana:", self.dias_sb)

        self.nivel_cb = QComboBox()
        self.nivel_cb.addItems(["Principiante", "Intermedio", "Avanzado"])
        form_layout.addRow("Nivel de Experiencia:", self.nivel_cb)

        self.enfoque_le = QLineEdit()
        form_layout.addRow("Grupos Musculares (Opcional):", self.enfoque_le)

        main_layout.addLayout(form_layout)

        self.results_text_edit = QTextEdit()
        self.results_text_edit.setReadOnly(True)
        self.results_text_edit.setPlaceholderText(
            "Aquí aparecerá tu plan de entrenamiento..."
        )
        main_layout.addWidget(self.results_text_edit, 1)

        self.generate_btn = QPushButton("Generar Plan")
        self.generate_btn.clicked.connect(self.on_generate_plan_clicked)
        main_layout.addWidget(self.generate_btn)

        self.worker = None

    def on_generate_plan_clicked(self) -> None:
        """Inicia la generación de planes en un hilo separado."""
        objetivo = self.objetivo_cb.currentText()
        dias = self.dias_sb.value()
        nivel = self.nivel_cb.currentText()
        enfoque = self.enfoque_le.text().strip()

        self.generate_btn.setEnabled(False)
        self.results_text_edit.setPlainText("Generando plan...")

        self.worker = PlanGeneratorWorker(objetivo, dias, nivel, enfoque)
        self.worker.finished.connect(self.on_plan_generation_finished)
        self.worker.error.connect(self.on_plan_generation_error)
        self.worker.start()

    def on_plan_generation_finished(self, plan_text: str) -> None:
        self.generate_btn.setEnabled(True)
        self.results_text_edit.setMarkdown(plan_text)

    def on_plan_generation_error(self, error_message: str) -> None:
        self.generate_btn.setEnabled(True)
        QMessageBox.critical(self, "Error generando plan", error_message)

