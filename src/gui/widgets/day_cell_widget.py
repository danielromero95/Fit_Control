from __future__ import annotations

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class DayCellWidget(QWidget):
    """Widget que representa una celda de día en el calendario."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("isToday", False)
        self.setProperty("isCurrentMonth", True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        self.day_label = QLabel("", self)
        self.day_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.day_label)

    def set_day(self, day_number: int, is_today: bool, is_current_month: bool) -> None:
        """Actualiza la celda con el número de día y su estado."""
        self.day_label.setText(str(day_number))
        self.setProperty("isToday", is_today)
        self.setProperty("isCurrentMonth", is_current_month)
        # Forzar repintado de estilos QSS
        self.style().unpolish(self)
        self.style().polish(self)
