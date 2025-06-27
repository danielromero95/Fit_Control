import os
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QScrollArea,
    QGridLayout,
    QApplication,
    QLabel,
    QHBoxLayout,
    QPushButton,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMovie
from pathlib import Path

from ..widgets.exercise_card_widget import ExerciseCardWidget
from ..widgets.collapsible_section import CollapsibleSection

from ... import database


class ExercisesPage(QWidget):
    """Biblioteca de ejercicios."""

    exercise_selected = pyqtSignal(int)

    def __init__(self, project_root: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.project_root = project_root

        layout = QVBoxLayout(self)

        controls_layout = QHBoxLayout()
        self.group_combo = QComboBox()
        controls_layout.addWidget(self.group_combo)
        self.expand_all_btn = QPushButton("Expand All")
        self.collapse_all_btn = QPushButton("Collapse All")
        controls_layout.addWidget(self.expand_all_btn)
        controls_layout.addWidget(self.collapse_all_btn)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)

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
        self.expand_all_btn.clicked.connect(self.expand_all)
        self.collapse_all_btn.clicked.connect(self.collapse_all)

        self.group_sections: dict[str, CollapsibleSection] = {}
        self.section_info: dict[str, dict[str, object]] = {}

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
        self._update_grid_columns()

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
            grid_container = QWidget()
            grid_layout = QGridLayout(grid_container)
            grid_layout.setContentsMargins(2, 2, 2, 2)
            grid_layout.setSpacing(8)

            exercises = database.get_exercises_by_group(grp)
            cards: list[ExerciseCardWidget] = []
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
                cards.append(card)

            section = CollapsibleSection(grp, grid_container)
            self.scroll_layout.addWidget(section)
            self.group_sections[grp] = section
            self.section_info[grp] = {
                "layout": grid_layout,
                "cards": cards,
                "container": grid_container,
            }

    def _update_grid_columns(self) -> None:
        """Reorganize cards based on the available width."""
        width = self.scroll_area.viewport().width()
        columns = max(3, min(6, width // 200))
        for info in self.section_info.values():
            layout: QGridLayout = info["layout"]  # type: ignore[assignment]
            cards: list[ExerciseCardWidget] = info["cards"]  # type: ignore[assignment]

            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().setParent(info["container"])

            row = 0
            col = 0
            for card in cards:
                layout.addWidget(card, row, col)
                col += 1
                if col >= columns:
                    col = 0
                    row += 1

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._update_grid_columns()

    def expand_all(self) -> None:
        for section in self.group_sections.values():
            section.expand()

    def collapse_all(self) -> None:
        for section in self.group_sections.values():
            section.collapse()

