import os
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QScrollArea,
    QGridLayout,
    QApplication,
    QLabel,
    QHBoxLayout,
    QPushButton,
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
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
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar ejercicio...")
        self.search_input.setObjectName("exerciseSearchInput")
        self.search_input.setClearButtonEnabled(True)
        controls_layout.addWidget(self.search_input)
        controls_layout.addStretch()
        self.expand_all_btn = QPushButton("Expand All")
        self.collapse_all_btn = QPushButton("Collapse All")
        controls_layout.addWidget(self.expand_all_btn)
        controls_layout.addWidget(self.collapse_all_btn)
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

        self.no_results_label = QLabel("No se encontraron ejercicios que coincidan con tu b\u00fasqueda.")
        self.no_results_label.setAlignment(Qt.AlignCenter)
        self.no_results_label.hide()
        layout.addWidget(self.no_results_label)

        self.container = QWidget()
        self.scroll_layout = QVBoxLayout(self.container)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(10)
        self.scroll_area.setWidget(self.container)

        self.search_timer = QTimer(self)
        self.search_timer.setInterval(250)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(lambda: self._on_search_query_changed(self.search_input.text()))
        self.search_input.textChanged.connect(self._restart_search_timer)
        self.expand_all_btn.clicked.connect(self.expand_all)
        self.collapse_all_btn.clicked.connect(self.collapse_all)

        self.group_sections: dict[str, CollapsibleSection] = {}
        self.section_info: dict[str, dict[str, object]] = {}

        self.refresh_groups()

    def refresh_groups(self) -> None:
        """Carga los grupos musculares y reconstruye la vista."""
        groups = database.get_all_muscle_groups()

        self.scroll_area.hide()
        self.loading_label.show()
        self.loading_movie.start()
        QApplication.processEvents()

        self._build_sections(groups)
        self._update_grid_columns()

        self.loading_movie.stop()
        self.loading_label.hide()
        self.scroll_area.show()


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

    # --------------------------------------------------------------
    def _restart_search_timer(self, _text: str) -> None:
        """Restart the debounce timer for search."""
        self.search_timer.stop()
        self.search_timer.start()

    # --------------------------------------------------------------
    def _on_search_query_changed(self, text: str) -> None:
        """Filter exercise cards based on the search query."""
        query = text.lower().strip()
        any_section_visible = False
        for group, info in self.section_info.items():
            cards: list[ExerciseCardWidget] = info["cards"]  # type: ignore[assignment]
            section = self.group_sections.get(group)
            if section is None:
                continue

            any_visible = False
            for card in cards:
                name = card.raw_name.lower()
                if query in name:
                    card.show()
                    card.highlight(query)
                    any_visible = True
                else:
                    card.hide()
                    card.highlight("")

            if any_visible:
                section.show()
                any_section_visible = True
            else:
                section.hide()

        if any_section_visible:
            self.no_results_label.hide()
            self.scroll_area.show()
        else:
            self.scroll_area.hide()
            self.no_results_label.show()

