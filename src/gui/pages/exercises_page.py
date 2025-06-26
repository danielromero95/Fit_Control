from PyQt5.QtWidgets import QWidget, QHBoxLayout, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal

from ... import database


class ExercisesPage(QWidget):
    """Biblioteca de ejercicios."""

    exercise_selected = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QHBoxLayout(self)

        self.group_list = QListWidget()
        layout.addWidget(self.group_list)

        self.exercise_list = QListWidget()
        layout.addWidget(self.exercise_list, 1)

        self.group_list.itemClicked.connect(self.on_group_selected)
        self.exercise_list.itemDoubleClicked.connect(self.on_exercise_double_clicked)

        self.refresh_groups()

    def refresh_groups(self) -> None:
        """Carga los grupos musculares y muestra los ejercicios del primero."""
        self.group_list.clear()
        groups = database.get_all_muscle_groups()
        self.group_list.addItem("Todos")
        for g in groups:
            self.group_list.addItem(g)
        self.group_list.setCurrentRow(0)
        if self.group_list.count() > 0:
            self.on_group_selected(self.group_list.item(0))

    def on_group_selected(self, item: QListWidgetItem) -> None:
        group = item.text()
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

