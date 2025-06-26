from __future__ import annotations

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal


class DayCellWidget(QWidget):
    """Widget que representa una celda de día en el calendario."""

    clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("isToday", False)
        self.setProperty("isCurrentMonth", True)
        self.setProperty("isSelected", False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        self.day_label = QLabel("", self)
        self.day_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.day_label)

    # --------------------------------------------------------------
    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def set_day(self, day_number: int, *, is_current_month: bool) -> None:
        """Actualiza la celda con el número de día y su estado."""
        self.day_label.setText(str(day_number))
        self.setProperty("isCurrentMonth", is_current_month)
        # Forzar repintado de estilos QSS
        self.style().unpolish(self)
        self.style().polish(self)
