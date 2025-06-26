from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGridLayout,
)
from PyQt5.QtCore import QDate, Qt, pyqtSignal

from .day_cell_widget import DayCellWidget


class CustomCalendarWidget(QWidget):
    """Calendario personalizado basado en DayCellWidget."""

    date_selected = pyqtSignal(QDate)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._current_date = QDate.currentDate()
        self._selected_date = self._current_date
        self._selected_cell: DayCellWidget | None = None
        self._cell_dates: dict[DayCellWidget, QDate] = {}

        main_layout = QVBoxLayout(self)

        # ----- Cabecera de navegación -----
        header_container = QWidget()
        header_container.setObjectName("calendarHeaderContainer")
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        self.prev_button = QPushButton("<")
        self.prev_button.setObjectName("calendarNavButton")
        self.next_button = QPushButton(">")
        self.next_button.setObjectName("calendarNavButton")
        self.header_label = QLabel()
        self.header_label.setObjectName("calendarHeader")
        self.header_label.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(self.prev_button)
        header_layout.addWidget(self.header_label)
        header_layout.addWidget(self.next_button)
        main_layout.addWidget(header_container)

        # ----- Encabezado de días de la semana -----
        week_layout = QGridLayout()
        week_layout.setSpacing(2)
        day_names = ["L", "M", "X", "J", "V", "S", "D"]
        for i, name in enumerate(day_names):
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignCenter)
            week_layout.addWidget(lbl, 0, i)
        main_layout.addLayout(week_layout)

        # ----- Grid de días -----
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(2)
        main_layout.addLayout(self.grid_layout)

        self.day_cells: list[DayCellWidget] = []
        for row in range(6):
            for col in range(7):
                cell = DayCellWidget()
                # DayCellWidget.clicked emits no parameters, so the connected
                # slot must not expect any. Passing the cell explicitly avoids
                # a TypeError when the signal is emitted.
                cell.clicked.connect(lambda c=cell: self._on_cell_clicked(c))
                self.grid_layout.addWidget(cell, row, col)
                self.day_cells.append(cell)

        # Conexiones de navegación
        self.prev_button.clicked.connect(self._go_prev_month)
        self.next_button.clicked.connect(self._go_next_month)

        self.populate_month(self._current_date.year(), self._current_date.month())
        # Seleccionamos la fecha actual por defecto
        for cell, date in self._cell_dates.items():
            if date == self._selected_date:
                self._on_cell_clicked(cell)
                break

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
        next_month = first_day.addMonths(1)

        today = QDate.currentDate()

        self._cell_dates.clear()
        self._selected_cell = None
        index = 0
        # Días del mes anterior
        for i in range(start_day - 1):
            day_num = days_in_prev - start_day + 2 + i
            cell = self.day_cells[index]
            cell.set_day(day_num, False, False)
            cell.setProperty("isSelected", False)
            date = QDate(prev_month.year(), prev_month.month(), day_num)
            self._cell_dates[cell] = date
            index += 1

        # Días del mes actual
        for day in range(1, days_in_month + 1):
            is_today = (
                day == today.day() and month == today.month() and year == today.year()
            )
            cell = self.day_cells[index]
            cell.set_day(day, is_today, True)
            date = QDate(year, month, day)
            is_selected = date == self._selected_date
            cell.setProperty("isSelected", is_selected)
            if is_selected:
                self._selected_cell = cell
            else:
                cell.setProperty("isSelected", False)
            self._cell_dates[cell] = date
            index += 1

        # Días del mes siguiente
        next_day = 1
        while index < len(self.day_cells):
            cell = self.day_cells[index]
            cell.set_day(next_day, False, False)
            cell.setProperty("isSelected", False)
            date = QDate(next_month.year(), next_month.month(), next_day)
            self._cell_dates[cell] = date
            next_day += 1
            index += 1

        # Reaplicar estilos
        for cell in self.day_cells:
            cell.style().unpolish(cell)
            cell.style().polish(cell)

    # ------------------------------------------------------------------
    def _go_prev_month(self) -> None:
        self._selected_date = self._selected_date.addMonths(-1)
        new_month_date = QDate(
            self._selected_date.year(), self._selected_date.month(), 1
        )
        self.populate_month(new_month_date.year(), new_month_date.month())
        for cell, date in self._cell_dates.items():
            if date == self._selected_date:
                self._on_cell_clicked(cell)
                break

    def _go_next_month(self) -> None:
        self._selected_date = self._selected_date.addMonths(1)
        new_month_date = QDate(
            self._selected_date.year(), self._selected_date.month(), 1
        )
        self.populate_month(new_month_date.year(), new_month_date.month())
        for cell, date in self._cell_dates.items():
            if date == self._selected_date:
                self._on_cell_clicked(cell)
                break

    # ------------------------------------------------------------------
    def _on_cell_clicked(self, cell: DayCellWidget) -> None:
        if cell not in self._cell_dates:
            return
        if self._selected_cell is not None:
            self._selected_cell.setProperty("isSelected", False)
            self._selected_cell.style().unpolish(self._selected_cell)
            self._selected_cell.style().polish(self._selected_cell)

        self._selected_cell = cell
        self._selected_date = self._cell_dates[cell]
        cell.setProperty("isSelected", True)
        cell.style().unpolish(cell)
        cell.style().polish(cell)
        self.update()
        self.date_selected.emit(self._selected_date)
