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
                # Conectamos la señal 'clicked' de la celda a nuestro manejador
                cell.clicked.connect(lambda c=cell: self._on_cell_clicked(c))
                self.grid_layout.addWidget(cell, row, col)
                self.day_cells.append(cell)

        self.prev_button.clicked.connect(self._go_prev_month)
        self.next_button.clicked.connect(self._go_next_month)

        self.populate_month(self._current_date.year(), self._current_date.month())

    def populate_month(self, year: int, month: int) -> None:
        """Rellena el calendario con los días del mes especificado."""
        self.header_label.setText(f"{QDate(year, month, 1).toString('MMMM yyyy').capitalize()}")
        
        first_day = QDate(year, month, 1)
        prev_month = first_day.addMonths(-1)
        next_month = first_day.addMonths(1)
        
        days_in_prev_month = prev_month.daysInMonth()
        start_day_of_week = first_day.dayOfWeek() -1 # Lunes=0, Domingo=6

        # Días del mes anterior
        for i in range(start_day_of_week):
            day = days_in_prev_month - start_day_of_week + i + 1
            cell = self.day_cells[i]
            cell.set_day(day, is_current_month=False)
            self._cell_dates[cell] = QDate(prev_month.year(), prev_month.month(), day)

        # Días del mes actual
        days_in_month = first_day.daysInMonth()
        for i in range(days_in_month):
            day = i + 1
            cell = self.day_cells[start_day_of_week + i]
            cell.set_day(day, is_current_month=True)
            self._cell_dates[cell] = QDate(year, month, day)

        # Días del mes siguiente
        day_index = start_day_of_week + days_in_month
        next_day = 1
        while day_index < len(self.day_cells):
            cell = self.day_cells[day_index]
            cell.set_day(next_day, is_current_month=False)
            self._cell_dates[cell] = QDate(next_month.year(), next_month.month(), next_day)
            next_day += 1
            day_index += 1
            
        self._update_cell_states()

    def _update_cell_states(self) -> None:
        """Actualiza las propiedades 'isToday' y 'isSelected' de todas las celdas."""
        today = QDate.currentDate()
        for cell, date in self._cell_dates.items():
            cell.setProperty("isToday", date == today)
            cell.setProperty("isSelected", date == self._selected_date)
        self._refresh_styles()

    def _refresh_styles(self) -> None:
        """Fuerza la re-evaluación de los estilos de todas las celdas."""
        for cell in self.day_cells:
            cell.style().unpolish(cell)
            cell.style().polish(cell)
        self.update()

    def _go_prev_month(self) -> None:
        self._current_date = self._current_date.addMonths(-1)
        self.populate_month(self._current_date.year(), self._current_date.month())

    def _go_next_month(self) -> None:
        self._current_date = self._current_date.addMonths(1)
        self.populate_month(self._current_date.year(), self._current_date.month())

    def _on_cell_clicked(self, cell: DayCellWidget) -> None:
        """Manejador para cuando se hace clic en una celda."""
        if cell not in self._cell_dates:
            return

        clicked_date = self._cell_dates[cell]
        
        # Si la fecha pertenece al mes anterior/siguiente, cambia de mes
        if clicked_date.month() != self._current_date.month():
            self._current_date = clicked_date
            self._selected_date = clicked_date
            self.populate_month(self._current_date.year(), self._current_date.month())
        else:
            self._selected_date = clicked_date
            self._update_cell_states()
        
        self.date_selected.emit(self._selected_date)
