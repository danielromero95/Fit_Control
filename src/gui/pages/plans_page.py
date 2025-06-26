from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QInputDialog,
    QLabel,
    QStackedWidget,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie, QColor
from PyQt5.QtWidgets import QMessageBox
from datetime import datetime

from ...services.plan_generator import PlanGeneratorWorker
from ... import database
from ..main import translator


class PlansPage(QWidget):
    """Página para generar planes de entrenamiento personalizados."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        main_layout = QHBoxLayout(self)

        # ----- Left column -----
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

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
        form_layout.addRow(translator.tr("main_goal"), self.objetivo_cb)

        self.dias_sb = QSpinBox()
        self.dias_sb.setRange(1, 7)
        self.dias_sb.setValue(3)
        form_layout.addRow("Días por Semana:", self.dias_sb)

        self.nivel_cb = QComboBox()
        self.nivel_cb.addItems(["Principiante", "Intermedio", "Avanzado"])
        form_layout.addRow("Nivel de Experiencia:", self.nivel_cb)

        self.enfoque_le = QLineEdit()
        form_layout.addRow("Grupos Musculares (Opcional):", self.enfoque_le)

        left_layout.addLayout(form_layout)

        self.saved_plans_list = QListWidget()
        left_layout.addWidget(self.saved_plans_list, 1)

        self.refresh_btn = QPushButton("Actualizar Lista")
        left_layout.addWidget(self.refresh_btn)

        main_layout.addWidget(left_widget)

        # ----- Right column -----
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

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

        right_layout.addWidget(self.results_stack, 1)

        self.save_plan_btn = QPushButton(translator.tr("save_plan"))
        self.save_plan_btn.setEnabled(False)
        self.save_plan_btn.setToolTip("Guardar el plan mostrado en tu historial")
        right_layout.addWidget(self.save_plan_btn)

        self.set_active_btn = QPushButton("Establecer como Plan Activo")
        self.set_active_btn.setEnabled(False)
        self.set_active_btn.setToolTip(translator.tr("active_plan_tooltip"))
        right_layout.addWidget(self.set_active_btn)

        self.generate_btn = QPushButton(translator.tr("generate_plan"))
        self.generate_btn.setToolTip("Generar un nuevo plan de entrenamiento con IA")
        self.generate_btn.clicked.connect(self.on_generate_plan_clicked)
        left_layout.addWidget(self.generate_btn)

        main_layout.addWidget(right_widget, 1)

        self.worker = None

        self.refresh_btn.clicked.connect(self.refresh_saved_plans)
        self.save_plan_btn.clicked.connect(self.on_save_plan_clicked)
        self.set_active_btn.clicked.connect(self.on_set_active_plan)
        self.saved_plans_list.itemClicked.connect(self.on_saved_plan_selected)
        self.refresh_saved_plans()

    def on_generate_plan_clicked(self) -> None:
        """Inicia la generación de planes en un hilo separado."""
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
        self.save_plan_btn.setEnabled(True)

    def on_plan_generation_error(self, error_message: str) -> None:
        self.generate_btn.setEnabled(True)
        self.loading_movie.stop()
        self.results_stack.setCurrentWidget(self.results_text_edit)
        QMessageBox.critical(self, "Error generando plan", error_message)

    def refresh_saved_plans(self) -> None:
        """Carga los planes almacenados en la base de datos."""
        self.saved_plans_list.clear()
        rows = database.get_all_training_plans()
        active_plan_id = database.get_active_plan_id()
        for row in rows:
            try:
                ts = datetime.fromisoformat(row["timestamp"])
                formatted = ts.strftime("%d %b %Y - %H:%M")
            except Exception:
                formatted = row["timestamp"]
            item_text = f"{row['title']} - {formatted}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, row["id"])
            if active_plan_id is not None and row["id"] == active_plan_id:
                item.setBackground(QColor("#5a9"))
            self.saved_plans_list.addItem(item)
        self.set_active_btn.setEnabled(self.saved_plans_list.count() > 0)

    def on_save_plan_clicked(self) -> None:
        """Solicita un título y guarda el plan actual."""
        if not self.results_text_edit.toPlainText().strip():
            return
        title, ok = QInputDialog.getText(self, "Guardar Plan", "Título del plan:")
        if ok and title.strip():
            database.save_training_plan(title.strip(), self.results_text_edit.toMarkdown())
            self.save_plan_btn.setEnabled(False)
            window = self.window()
            if hasattr(window, "statusBar"):
                window.statusBar().showMessage("Plan guardado", 5000)
            self.refresh_saved_plans()

    def on_saved_plan_selected(self, item: QListWidgetItem) -> None:
        plan_id = item.data(Qt.UserRole)
        row = database.get_plan_by_id(int(plan_id))
        if row:
            self.results_text_edit.setMarkdown(row.get("plan_content_md", ""))
            self.save_plan_btn.setEnabled(False)
        self.set_active_btn.setEnabled(True)

    def on_set_active_plan(self) -> None:
        """Establece el plan seleccionado como activo en el estado global."""
        item = self.saved_plans_list.currentItem()
        if not item:
            return
        plan_id = item.data(Qt.UserRole)
        database.set_app_state("active_plan_id", str(plan_id))
        window = self.window()
        if hasattr(window, "statusBar"):
            window.statusBar().showMessage("Plan activo actualizado", 5000)
        self.refresh_saved_plans()

