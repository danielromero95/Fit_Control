# src/gui/widgets/video_display.py
import os
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal

class VideoDisplayWidget(QWidget):
    """
    Un widget para arrastrar, soltar y mostrar un thumbnail de vídeo,
    ahora con controles de rotación interactivos.
    """
    file_dropped = pyqtSignal(str)
    rotation_requested = pyqtSignal(int)  # Señal que emite +90 o -90

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.default_text = "Arrastra o selecciona tu vídeo aquí"
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)

        # Widget para la imagen
        self.image_label = QLabel(self.default_text, self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("color: #777; font-size: 16px; background: transparent;")
        main_layout.addWidget(self.image_label)

        # Layout para los botones de control (inicialmente oculto)
        self.controls_layout = QHBoxLayout()
        self.rotate_left_btn = QPushButton("↺ Girar Izquierda")
        self.rotate_right_btn = QPushButton("Girar Derecha ↻")
        self.controls_layout.addStretch()
        self.controls_layout.addWidget(self.rotate_left_btn)
        self.controls_layout.addWidget(self.rotate_right_btn)
        self.controls_layout.addStretch()
        
        # Añadir el layout de controles al layout principal
        main_layout.addLayout(self.controls_layout)
        
        # Conectar señales de los botones
        self.rotate_left_btn.clicked.connect(lambda: self.rotation_requested.emit(-90))
        self.rotate_right_btn.clicked.connect(lambda: self.rotation_requested.emit(90))

        # Estilos
        self.normal_style = "VideoDisplayWidget { border: 2px dashed #aaa; border-radius: 8px; }"
        self.dragover_style = "VideoDisplayWidget { border: 2px dashed #0078d7; border-radius: 8px; background-color: #e8f0fe; }"
        self.setStyleSheet(self.normal_style)
        
        self.show_controls(False) # Ocultar controles al inicio

    def show_controls(self, show: bool):
        """Muestra u oculta los botones de rotación."""
        self.rotate_left_btn.setVisible(show)
        self.rotate_right_btn.setVisible(show)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self.setStyleSheet(self.dragover_style)
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(self.normal_style)

    def dropEvent(self, event):
        self.setStyleSheet(self.normal_style)
        if event.mimeData().hasUrls():
            path = event.mimeData().urls()[0].toLocalFile()
            if os.path.isfile(path):
                self.file_dropped.emit(path)

    def set_thumbnail(self, pixmap):
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)
        self.show_controls(True) # Mostrar controles cuando hay una imagen

    def clear_content(self):
        self.image_label.clear()
        self.image_label.setText(self.default_text)
        self.show_controls(False) # Ocultar controles cuando se limpia