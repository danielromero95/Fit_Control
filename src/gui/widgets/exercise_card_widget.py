from __future__ import annotations
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QStyle
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap


class ExerciseCardWidget(QWidget):
    """
    Tarjeta visual robusta para un ejercicio.
    Gestiona el escalado de imagen dinámicamente.
    """

    clicked = pyqtSignal(int)

    def __init__(self, ex_id: int, name: str, icon_path: str | None, equipment: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.exercise_id = ex_id
        self.image_path = icon_path or ""

        # --- Configuración del Widget Principal ---
        self.setObjectName("ExerciseCardWidget")
        self.setMinimumSize(180, 180)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)

        # --- Layout y Contenido ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label, 3)

        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)

        self.name_label = QLabel(name)
        self.name_label.setObjectName("exerciseCardName")
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        text_layout.addWidget(self.name_label)

        if equipment:
            self.equipment_label = QLabel(equipment)
            self.equipment_label.setObjectName("exerciseCardEquipment")
            self.equipment_label.setAlignment(Qt.AlignCenter)
            text_layout.addWidget(self.equipment_label)

        layout.addWidget(text_container, 1)

        self.original_pixmap = self._load_original_pixmap()

    def _load_original_pixmap(self) -> QPixmap:
        """Carga la imagen original desde el disco una sola vez."""
        pixmap = QPixmap(self.image_path)
        if pixmap.isNull():
            icon = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
            return icon.pixmap(64, 64)
        return pixmap

    def resizeEvent(self, event) -> None:
        """
        Este evento se dispara cada vez que el widget cambia de tamaño.
        Aquí es donde debemos re-escalar la imagen.
        """
        super().resizeEvent(event)
        if self.original_pixmap:
            scaled_pixmap = self.original_pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

    def mousePressEvent(self, event) -> None:
        """Emite la señal de clic."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.exercise_id)
        super().mousePressEvent(event)
