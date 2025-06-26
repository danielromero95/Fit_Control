import os
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QScrollArea,
    QLabel,
    QHBoxLayout,
    QApplication,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMovie
from pathlib import Path

from ..widgets.exercise_card_widget import ExerciseCardWidget

from ... import database


class ExercisesPage(QWidget):
    """Biblioteca de ejercicios."""

    exercise_selected = pyqtSignal(int)

    def __init__(self, project_root: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.project_root = project_root

        layout = QVBoxLayout(self)

        self.group_combo = QComboBox()
        layout.addWidget(self.group_combo)

        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_movie = QMovie(str(Path('assets') / 'Gym_Loading_Gif.gif'))
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.hide()
        layout.addWidget(self.loading_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area, 1)

        self.container = QWidget()
        self.scroll_layout = QVBoxLayout(self.container)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(10)
        self.scroll_area.setWidget(self.container)

        self.group_combo.currentTextChanged.connect(self.on_group_selected)

        self.group_sections: dict[str, QWidget] = {}

        self.refresh_groups()

    def refresh_groups(self) -> None:
        """Carga los grupos musculares y reconstruye la vista."""
        self.group_combo.clear()
        groups = database.get_all_muscle_groups()
        for g in groups:
            self.group_combo.addItem(g)

        self.scroll_area.hide()
        self.loading_label.show()
        self.loading_movie.start()
        QApplication.processEvents()

        self._build_sections(groups)

        self.loading_movie.stop()
        self.loading_label.hide()
        self.scroll_area.show()

        if self.group_combo.count() > 0:
            self.group_combo.setCurrentIndex(0)

    def on_group_selected(self, group: str) -> None:
        section = self.group_sections.get(group)
        if section is not None:
            self.scroll_area.ensureWidgetVisible(section, yMargin=10)

    def _build_sections(self, groups: list[str]) -> None:
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.group_sections.clear()

        for grp in groups:
            title = QLabel(grp)
            title.setObjectName("muscleGroupTitle")
            self.scroll_layout.addWidget(title)
            self.group_sections[grp] = title

            ex_scroll = QScrollArea()
            ex_scroll.setWidgetResizable(True)
            ex_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            ex_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

            cont = QWidget()
            h_layout = QHBoxLayout(cont)
            h_layout.setContentsMargins(2, 2, 2, 2)
            h_layout.setSpacing(8)

            ex_scroll.setWidget(cont)
            self.scroll_layout.addWidget(ex_scroll)

            exercises = database.get_exercises_by_group(grp)
            for ex in exercises:
                icon_path_relative = ex.get("icon_path", "")
                icon_path_absolute = ""
                if icon_path_relative:
                    icon_path_absolute = os.path.join(self.project_root, icon_path_relative)
                    print(f"DEBUG: Intentando cargar icono desde: {icon_path_absolute}")

                card = ExerciseCardWidget(
                    int(ex["id"]),
                    ex["name"],
                    icon_path_absolute,
                    ex.get("equipment"),
                )
                card.clicked.connect(self.exercise_selected)
                h_layout.addWidget(card)

            h_layout.addStretch(1)

