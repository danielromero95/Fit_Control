from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class PlansPage(QWidget):
    """Página placeholder para planes de entrenamiento y nutrición."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("Sección de Planes próximamente")
        label.setAlignment(Qt.AlignCenter)
        layout.addStretch(1)
        layout.addWidget(label)
        layout.addStretch(1)

