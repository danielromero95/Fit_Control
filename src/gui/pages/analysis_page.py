from typing import Callable
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QProgressBar, QLabel
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from ..widgets.video_display import VideoDisplayWidget


class AnalysisPage(QWidget):
    """Página para cargar y analizar un video."""

    def __init__(
        self,
        on_video_selected: Callable[[str], None],
        on_rotation_requested: Callable[[int], None],
        on_open_file_dialog: Callable[[], None],
        on_start_analysis: Callable[[], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)

        video_container = QWidget()
        video_container.setFixedHeight(400)
        video_layout = QVBoxLayout(video_container)
        video_layout.setContentsMargins(0, 0, 0, 0)

        self.video_display = VideoDisplayWidget()
        self.video_display.file_dropped.connect(on_video_selected)
        self.video_display.rotation_requested.connect(on_rotation_requested)
        video_layout.addWidget(self.video_display)
        layout.addWidget(video_container)

        self.select_video_btn = QPushButton("Seleccionar Vídeo...")
        self.select_video_btn.clicked.connect(on_open_file_dialog)
        layout.addWidget(self.select_video_btn)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.results_label = QLabel("Arrastra un vídeo o selecciónalo para empezar")
        self.results_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(12)
        self.results_label.setFont(font)
        layout.addWidget(self.results_label)

        self.process_btn = QPushButton("Analizar Vídeo")
        self.process_btn.setEnabled(False)
        self.process_btn.clicked.connect(on_start_analysis)
        layout.addWidget(self.process_btn)

