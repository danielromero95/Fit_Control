# src/gui/widgets/video_display.py
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal

class VideoDisplayWidget(QWidget):
    """Un widget para arrastrar, soltar y mostrar un thumbnail de vídeo."""
    file_dropped = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.default_text = "Arrastra o selecciona tu vídeo aquí"
        self.label = QLabel(self.default_text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: #777; font-size: 16px; background: transparent;")
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        
        self.normal_style = "VideoDisplayWidget { border: 2px dashed #aaa; border-radius: 8px; }"
        self.dragover_style = "VideoDisplayWidget { border: 2px dashed #0078d7; border-radius: 8px; background-color: #e8f0fe; }"
        self.setStyleSheet(self.normal_style)

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

    def show_thumbnail(self, pixmap):
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)

    def clear_content(self):
        self.label.clear()
        self.label.setText(self.default_text)