from __future__ import annotations

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QStyle
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap


class ExerciseCardWidget(QWidget):
    """Tarjeta visual para un ejercicio individual."""

    clicked = pyqtSignal(int)

    def __init__(self, ex_id: int, name: str, icon_path: str | None, equipment: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.exercise_id = ex_id
        self.image_path = icon_path or ""

        self.setObjectName("ExerciseCardWidget")
        self.setFixedSize(150, 180)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedHeight(120)
        layout.addWidget(self.image_label)

        self.name_label = QLabel(name)
        self.name_label.setObjectName("exerciseCardName")
        self.name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.name_label)

        self.equipment_label: QLabel | None = None
        if equipment:
            self.equipment_label = QLabel(equipment)
            self.equipment_label.setObjectName("exerciseCardEquipment")
            self.equipment_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.equipment_label)

        self._load_image()

    # --------------------------------------------------
    def _load_image(self) -> None:
        pix = None
        if self.image_path and os.path.exists(self.image_path):
            tmp = QPixmap(self.image_path)
            if not tmp.isNull():
                pix = tmp
        if pix is None:
            icon = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
            pix = icon.pixmap(self.image_label.size())

        self.image_label.setPixmap(
            pix.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    def resizeEvent(self, event):  # pragma: no cover - UI code
        super().resizeEvent(event)
        self._load_image()

    def mousePressEvent(self, event):  # pragma: no cover - UI interaction
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.exercise_id)
        super().mousePressEvent(event)
