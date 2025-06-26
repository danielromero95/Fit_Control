from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class ContactPage(QWidget):
    """Página de información de contacto (placeholder)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("Información de contacto próximamente")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

