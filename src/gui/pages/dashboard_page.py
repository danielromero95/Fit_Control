from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class DashboardPage(QWidget):
    """Página de bienvenida."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        label = QLabel("Bienvenido a Gym Performance Analyzer")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        label.setFont(font)
        label.setAlignment(Qt.AlignCenter)
        layout.addStretch(1)
        layout.addWidget(label)
        layout.addStretch(1)

