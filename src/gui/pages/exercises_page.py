from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QListWidget,
    QListWidgetItem,
)
from PyQt5.QtCore import Qt, pyqtSignal

from ... import database


class ExercisesPage(QWidget):
    """Biblioteca de ejercicios."""

    exercise_selected = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.group_combo = QComboBox()
        layout.addWidget(self.group_combo)

        self.exercise_list = QListWidget()
        layout.addWidget(self.exercise_list, 1)

        self.group_combo.currentTextChanged.connect(self.on_group_changed)
        self.exercise_list.itemDoubleClicked.connect(self.on_exercise_double_clicked)

        self.refresh_groups()

    def refresh_groups(self) -> None:
        """Carga la lista de grupos musculares en el combo."""
        self.group_combo.clear()
        groups = database.get_all_muscle_groups()
        self.group_combo.addItem("Todos")
        for g in groups:
            self.group_combo.addItem(g)
        if self.group_combo.count() > 0:
            self.group_combo.setCurrentIndex(0)
            self.refresh_exercises()

    def on_group_changed(self, group: str) -> None:
        self.refresh_exercises()

    def refresh_exercises(self) -> None:
        group = self.group_combo.currentText()
        self.exercise_list.clear()
        exercises = database.get_exercises_by_group(group)
        for ex in exercises:
            it = QListWidgetItem(ex["name"])
            it.setData(Qt.UserRole, ex["id"])
            self.exercise_list.addItem(it)

    def on_exercise_double_clicked(self, item: QListWidgetItem) -> None:
        ex_id = item.data(Qt.UserRole)
        if ex_id is not None:
            self.exercise_selected.emit(int(ex_id))

