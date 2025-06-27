from __future__ import annotations

from datetime import date, timedelta

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from typing import Iterable


class MiniCalendarWidget(QWidget):
    """Small, non-interactive calendar showing the current week."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._cells: list[tuple[QWidget, QLabel, QLabel]] = []
        self._workout_dates: set[date] = set()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        for _ in range(7):
            cell = QWidget()
            cell_layout = QVBoxLayout(cell)
            cell_layout.setContentsMargins(2, 2, 2, 2)
            cell_layout.setAlignment(Qt.AlignCenter)

            day_lbl = QLabel()
            day_lbl.setObjectName("miniCalDayName")
            day_lbl.setAlignment(Qt.AlignCenter)
            num_lbl = QLabel()
            num_lbl.setObjectName("miniCalDayNumber")
            num_lbl.setAlignment(Qt.AlignCenter)

            cell_layout.addWidget(day_lbl)
            cell_layout.addWidget(num_lbl)

            layout.addWidget(cell)
            self._cells.append((cell, day_lbl, num_lbl))

        self.update_week()

    # --------------------------------------------------------------
    def set_workout_dates(self, dates: Iterable[date]) -> None:
        self._workout_dates = set(dates)
        self.update_week()

    # --------------------------------------------------------------
    def update_week(self, ref_date: date | None = None) -> None:
        """Populate the widget with the week that contains ``ref_date``."""
        if ref_date is None:
            ref_date = date.today()
        start = ref_date - timedelta(days=ref_date.weekday())
        today = date.today()
        day_initials = ["L", "M", "X", "J", "V", "S", "D"]

        for i, (cell, day_lbl, num_lbl) in enumerate(self._cells):
            d = start + timedelta(days=i)
            day_lbl.setText(day_initials[i])
            num_lbl.setText(str(d.day))
            cell.setProperty("isToday", d == today)
            num_lbl.setProperty("hasWorkout", d in self._workout_dates)
            # Force style refresh
            cell.style().unpolish(cell)
            cell.style().polish(cell)

