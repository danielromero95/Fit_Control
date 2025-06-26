from __future__ import annotations
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QStyle
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap


class ExerciseCardWidget(QWidget):
    """Tarjeta visual para un ejercicio individual."""

    clicked = pyqtSignal(int)

    def __init__(self, ex_id: int, name: str, icon_path: str | None,
                 equipment: str | None = None,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.exercise_id = ex_id
        self.image_path = icon_path or ""
        self.name = name
        self.equipment = equipment

        self.setObjectName("ExerciseCardWidget")
        self.setFixedSize(160, 190)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedHeight(120)
        layout.addWidget(self.image_label)

        self.name_label = QLabel(self.name)
        self.name_label.setObjectName("exerciseCardName")
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)

        if self.equipment:
            self.equipment_label = QLabel(self.equipment)
            self.equipment_label.setObjectName("exerciseCardEquipment")
            self.equipment_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.equipment_label)

        layout.addStretch()

        self._load_and_scale_image()

    def _load_and_scale_image(self) -> None:
        """Carga y escala la imagen, con fallback a un icono de advertencia."""
        pixmap = QPixmap(self.image_path)
        if pixmap.isNull():
            icon = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
            pixmap = icon.pixmap(64, 64)

        scaled = pixmap.scaledToHeight(self.image_label.height(),
                                       Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled)

    def mousePressEvent(self, event):  # pragma: no cover - UI interaction
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.exercise_id)
        super().mousePressEvent(event)
