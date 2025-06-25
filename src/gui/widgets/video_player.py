# src/gui/widgets/video_player.py

import os
import logging
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QStyle, QComboBox, QLabel
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt, QTimer, pyqtSignal
from typing import Optional

logger = logging.getLogger(__name__)

class VideoPlayerWidget(QWidget):
    """
    Widget que encapsula un QMediaPlayer y sus controles. Implementa una señal
    de alta frecuencia para una sincronización fluida con otros widgets.
    """
    # Señal que emitirá la posición de forma continua para animaciones suaves
    smooth_position_changed = pyqtSignal(int)
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Inicializa el reproductor, los widgets y el timer de animación."""
        super().__init__(parent)
        self._was_playing_before_drag: bool = False
        
        # --- Creación de Widgets ---
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        video_widget = QVideoWidget()

        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        
        self.position_slider = QSlider(Qt.Horizontal)

        self.speed_combo = QComboBox()
        self.speed_combo.addItems(['0.25x', '0.5x', '1.0x', '1.5x', '2.0x'])
        
        # --- Timer para la animación fluida ---
        self.animation_timer = QTimer(self)
        self.animation_timer.setInterval(33)  # ~30 FPS
        self.animation_timer.timeout.connect(self._on_animation_tick)
        
        # --- Estado Inicial de los Controles ---
        self.clear_media()
        
        # --- Conexiones de Señales a Slots ---
        self.play_button.clicked.connect(self.toggle_play)
        self.position_slider.sliderMoved.connect(self.set_position_ms)
        self.position_slider.sliderPressed.connect(self._on_slider_press)
        self.position_slider.sliderReleased.connect(self._on_slider_release)
        self.speed_combo.currentTextChanged.connect(self.set_playback_rate)
        
        self.media_player.error.connect(self.handle_error)
        self.media_player.stateChanged.connect(self._on_state_changed)
        self.media_player.durationChanged.connect(self.update_slider_range)

        # --- Organización de Layouts ---
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.position_slider)
        controls_layout.addWidget(QLabel("Velocidad:"))
        controls_layout.addWidget(self.speed_combo)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(video_widget)
        main_layout.addLayout(controls_layout)
        
        self.media_player.setVideoOutput(video_widget)

    def _on_animation_tick(self) -> None:
        """Se ejecuta a ~30FPS mientras el vídeo se reproduce para emitir la posición."""
        pos = self.media_player.position()
        self.smooth_position_changed.emit(pos)
        # Actualizamos el slider desde aquí para total sincronización
        if not self.position_slider.isSliderDown():
            self.position_slider.setValue(pos)

    def _on_state_changed(self, state: QMediaPlayer.State) -> None:
        """Controla el timer de animación y el icono del botón según el estado del reproductor."""
        self.update_play_button_icon(state)
        if state == QMediaPlayer.PlayingState:
            self.animation_timer.start()
        else:
            self.animation_timer.stop()

    def load_video(self, video_path: str) -> None:
        """Carga un nuevo vídeo en el reproductor, fuerza la inicialización y activa los controles."""
        if video_path and os.path.exists(video_path):
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
            self.play_button.setEnabled(True)
            self.speed_combo.setEnabled(True)
            self.position_slider.setValue(0)
            self.set_playback_rate(self.speed_combo.currentText())
            # Forzamos la carga del buffer para que el vídeo esté listo para 'seek'
            self.media_player.play()
            self.media_player.pause()
        else:
            self.clear_media()

    def set_playback_rate(self, text: str) -> None:
        """Ajusta la velocidad de reproducción a partir del texto del ComboBox."""
        rate_str = text.replace('x', '')
        try:
            self.media_player.setPlaybackRate(float(rate_str))
        except ValueError:
            logger.error(f"Valor de velocidad no válido: {text}")

    def set_position_ms(self, position_ms: int) -> None:
        """Método público para saltar a un punto del vídeo en milisegundos."""
        self.media_player.setPosition(position_ms)

    def _on_slider_press(self) -> None:
        """Slot que se activa al hacer clic en el slider. Pausa el vídeo."""
        self._was_playing_before_drag = (self.media_player.state() == QMediaPlayer.PlayingState)
        self.media_player.pause()

    def _on_slider_release(self) -> None:
        """Slot que se activa al soltar el clic del slider. Reanuda si estaba en play."""
        if self._was_playing_before_drag:
            self.media_player.play()
        self._was_playing_before_drag = False

    def handle_error(self) -> None:
        """Maneja y loguea errores del reproductor multimedia."""
        if self.media_player.error() != QMediaPlayer.NoError:
            logger.error(f"ERROR DEL REPRODUCTOR: {self.media_player.errorString()}")

    def toggle_play(self) -> None:
        """Alterna entre reproducir y pausar el vídeo."""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def update_play_button_icon(self, state: QMediaPlayer.State) -> None:
        """Actualiza el icono del botón de play/pausa según el estado."""
        if state == QMediaPlayer.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
    
    def update_slider_range(self, duration: int) -> None:
        """Ajusta el rango del slider a la duración del vídeo."""
        self.position_slider.setRange(0, duration)
        
    def clear_media(self) -> None:
        """Limpia el reproductor y resetea todos los controles a su estado inicial."""
        self.animation_timer.stop()
        self.media_player.stop()
        self.media_player.setMedia(QMediaContent())
        self.play_button.setEnabled(False)
        self.speed_combo.setEnabled(False)
        self.speed_combo.setCurrentText('1.0x')
        self.position_slider.setRange(0, 0)
        self.position_slider.setValue(0)
