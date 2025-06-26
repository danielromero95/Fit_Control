from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGridLayout,
)
from PyQt5.QtCore import QDate, Qt

from .day_cell_widget import DayCellWidget


class CustomCalendarWidget(QWidget):
    """Calendario personalizado basado en DayCellWidget."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._current_date = QDate.currentDate()

        main_layout = QVBoxLayout(self)

        # ----- Cabecera de navegación -----
        header_layout = QHBoxLayout()
        self.prev_button = QPushButton("<")
        self.prev_button.setObjectName("calendarNavButton")
        self.next_button = QPushButton(">")
        self.next_button.setObjectName("calendarNavButton")
        self.header_label = QLabel()
        self.header_label.setObjectName("calendarHeader")
        self.header_label.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(self.prev_button)
        header_layout.addStretch()
        header_layout.addWidget(self.header_label)
        header_layout.addStretch()
        header_layout.addWidget(self.next_button)
        main_layout.addLayout(header_layout)

        # ----- Grid de días -----
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(2)
        main_layout.addLayout(self.grid_layout)

        self.day_cells: list[DayCellWidget] = []
        for row in range(6):
            for col in range(7):
                cell = DayCellWidget()
                self.grid_layout.addWidget(cell, row, col)
                self.day_cells.append(cell)

        # Conexiones de navegación
        self.prev_button.clicked.connect(self._go_prev_month)
        self.next_button.clicked.connect(self._go_next_month)

        self.populate_month(self._current_date.year(), self._current_date.month())

    # ------------------------------------------------------------------
    def populate_month(self, year: int, month: int) -> None:
        """Rellena el calendario con los días del mes especificado."""
        self._current_date = QDate(year, month, 1)
        self.header_label.setText(self._current_date.toString("MMMM yyyy"))

        first_day = QDate(year, month, 1)
        start_day = first_day.dayOfWeek()  # 1=Mon ... 7=Sun
        days_in_month = first_day.daysInMonth()

        prev_month = first_day.addMonths(-1)
        days_in_prev = prev_month.daysInMonth()

        today = QDate.currentDate()

        index = 0
        # Días del mes anterior
        for i in range(start_day - 1):
            day_num = days_in_prev - start_day + 2 + i
            self.day_cells[index].set_day(day_num, False, False)
            index += 1

        # Días del mes actual
        for day in range(1, days_in_month + 1):
            is_today = (
                day == today.day() and month == today.month() and year == today.year()
            )
            self.day_cells[index].set_day(day, is_today, True)
            index += 1

        # Días del mes siguiente
        next_day = 1
        while index < len(self.day_cells):
            self.day_cells[index].set_day(next_day, False, False)
            next_day += 1
            index += 1

    # ------------------------------------------------------------------
    def _go_prev_month(self) -> None:
        new_date = self._current_date.addMonths(-1)
        self.populate_month(new_date.year(), new_date.month())

    def _go_next_month(self) -> None:
        new_date = self._current_date.addMonths(1)
        self.populate_month(new_date.year(), new_date.month())
