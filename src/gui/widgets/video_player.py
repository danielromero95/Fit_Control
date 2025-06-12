# src/gui/widgets/video_player.py

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QStyle
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt # <-- ¡LA IMPORTACIÓN QUE FALTABA!

class VideoPlayerWidget(QWidget):
    """Un widget que encapsula un reproductor de vídeo con controles básicos."""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Crear los componentes multimedia
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        video_widget = QVideoWidget()

        # Crear botones de control
        self.play_button = QPushButton()
        self.play_button.setEnabled(False) # Deshabilitado hasta que se cargue un vídeo
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.toggle_play)

        # Crear slider para la posición del vídeo
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.sliderMoved.connect(self.set_position)

        # Conectar señales del reproductor
        self.media_player.stateChanged.connect(self.update_play_button_icon)
        self.media_player.positionChanged.connect(self.update_slider_position)
        self.media_player.durationChanged.connect(self.update_slider_range)

        # Diseñar el layout de los controles
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.position_slider)

        # Diseñar el layout principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(video_widget)
        main_layout.addLayout(controls_layout)
        self.setLayout(main_layout)
        
        # Conectar el reproductor a la superficie de vídeo
        self.media_player.setVideoOutput(video_widget)

    def load_video(self, video_path: str):
        """Carga un nuevo vídeo en el reproductor."""
        if video_path and os.path.exists(video_path):
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
            self.play_button.setEnabled(True)
            self.media_player.play()
        else:
            self.play_button.setEnabled(False)
            self.media_player.setMedia(QMediaContent())


    def toggle_play(self):
        """Alterna entre play y pausa."""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def update_play_button_icon(self, state):
        """Cambia el icono del botón de play/pausa."""
        if state == QMediaPlayer.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def set_position(self, position):
        """Mueve la reproducción a una nueva posición."""
        self.media_player.setPosition(position)

    def update_slider_position(self, position):
        """Actualiza la posición del slider."""
        self.position_slider.setValue(position)

    def update_slider_range(self, duration):
        """Actualiza el rango del slider."""
        self.position_slider.setRange(0, duration)