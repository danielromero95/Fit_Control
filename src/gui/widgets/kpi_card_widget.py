from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush, QColor
import qtawesome as qta


class KPICardWidget(QFrame):
    """Widget moderno para mostrar métricas KPI con iconos y tendencias."""
    
    clicked = pyqtSignal()
    
    def __init__(self, title: str, value: str, icon: str, trend: str = "", 
                 trend_positive: bool = True, color: str = "#3498db", parent=None):
        super().__init__(parent)
        
        self.title = title
        self.value = value
        self.icon = icon
        self.trend = trend
        self.trend_positive = trend_positive
        self.color = color
        
        self.setObjectName("KPICard")
        self.setFrameStyle(QFrame.Box)
        self.setCursor(Qt.PointingHandCursor)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura la interfaz del widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        # Header con icono y título
        header_layout = QHBoxLayout()
        
        # Icono
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon(self.icon, color=self.color).pixmap(24, 24))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(40, 40)
        icon_label.setObjectName("kpiIcon")
        
        # Título
        title_label = QLabel(self.title)
        title_label.setObjectName("kpiTitle")
        title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Valor principal
        value_label = QLabel(self.value)
        value_label.setObjectName("kpiValue")
        value_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        value_label.setAlignment(Qt.AlignLeft)
        
        # Tendencia
        trend_layout = QHBoxLayout()
        if self.trend:
            trend_icon = "fa5s.arrow-up" if self.trend_positive else "fa5s.arrow-down"
            trend_color = "#27ae60" if self.trend_positive else "#e74c3c"
            
            trend_icon_label = QLabel()
            trend_icon_label.setPixmap(qta.icon(trend_icon, color=trend_color).pixmap(12, 12))
            
            trend_text = QLabel(self.trend)
            trend_text.setObjectName("kpiTrend")
            trend_text.setFont(QFont("Segoe UI", 9))
            trend_text.setStyleSheet(f"color: {trend_color};")
            
            trend_layout.addWidget(trend_icon_label)
            trend_layout.addWidget(trend_text)
        
        trend_layout.addStretch()
        
        layout.addLayout(header_layout)
        layout.addWidget(value_label)
        layout.addLayout(trend_layout)
        
    def mousePressEvent(self, event):
        """Emite señal al hacer clic."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
        
    def update_value(self, new_value: str, new_trend: str = "", trend_positive: bool = True):
        """Actualiza el valor y tendencia del KPI."""
        self.value = new_value
        self.trend = new_trend
        self.trend_positive = trend_positive
        self._setup_ui()


class ProgressCardWidget(QFrame):
    """Widget para mostrar progreso con barra circular o lineal."""
    
    def __init__(self, title: str, current: int, total: int, 
                 unit: str = "", color: str = "#3498db", parent=None):
        super().__init__(parent)
        
        self.title = title
        self.current = current
        self.total = total
        self.unit = unit
        self.color = color
        
        self.setObjectName("ProgressCard")
        self.setFrameStyle(QFrame.Box)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura la interfaz del widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        # Título
        title_label = QLabel(self.title)
        title_label.setObjectName("progressTitle")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        
        # Valores
        values_layout = QHBoxLayout()
        current_label = QLabel(f"{self.current}")
        current_label.setObjectName("progressCurrent")
        current_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        
        separator_label = QLabel("/")
        separator_label.setObjectName("progressSeparator")
        separator_label.setFont(QFont("Segoe UI", 16))
        
        total_label = QLabel(f"{self.total} {self.unit}")
        total_label.setObjectName("progressTotal")
        total_label.setFont(QFont("Segoe UI", 14))
        
        values_layout.addWidget(current_label)
        values_layout.addWidget(separator_label)
        values_layout.addWidget(total_label)
        values_layout.addStretch()
        
        # Barra de progreso
        progress_bar = QFrame()
        progress_bar.setFixedHeight(6)
        progress_bar.setStyleSheet(f"""
            QFrame {{
                background-color: #ecf0f1;
                border-radius: 3px;
            }}
        """)
        
        # Progreso completado
        progress_percentage = (self.current / self.total * 100) if self.total > 0 else 0
        progress_fill = QFrame(progress_bar)
        fill_width = int(progress_bar.width() * progress_percentage / 100)
        progress_fill.setGeometry(0, 0, fill_width, 6)
        progress_fill.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color};
                border-radius: 3px;
            }}
        """)
        
        # Porcentaje
        percentage_label = QLabel(f"{int(progress_percentage)}%")
        percentage_label.setObjectName("progressPercentage")
        percentage_label.setFont(QFont("Segoe UI", 10))
        percentage_label.setAlignment(Qt.AlignRight)
        
        layout.addWidget(title_label)
        layout.addLayout(values_layout)
        layout.addWidget(progress_bar)
        layout.addWidget(percentage_label)
        
    def update_progress(self, current: int, total: int = None):
        """Actualiza el progreso."""
        self.current = current
        if total is not None:
            self.total = total
        self._setup_ui()


class QuickActionWidget(QFrame):
    """Widget para acciones rápidas con icono y descripción."""
    
    clicked = pyqtSignal()
    
    def __init__(self, title: str, description: str, icon: str, 
                 color: str = "#3498db", parent=None):
        super().__init__(parent)
        
        self.title = title
        self.description = description
        self.icon = icon
        self.color = color
        
        self.setObjectName("QuickActionCard")
        self.setFrameStyle(QFrame.Box)
        self.setCursor(Qt.PointingHandCursor)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura la interfaz del widget."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Icono
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon(self.icon, color=self.color).pixmap(32, 32))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(50, 50)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.color}20;
                border-radius: 25px;
            }}
        """)
        
        # Contenido
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        
        title_label = QLabel(self.title)
        title_label.setObjectName("actionTitle")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        
        desc_label = QLabel(self.description)
        desc_label.setObjectName("actionDescription")
        desc_label.setFont(QFont("Segoe UI", 10))
        desc_label.setWordWrap(True)
        
        content_layout.addWidget(title_label)
        content_layout.addWidget(desc_label)
        
        # Flecha
        arrow_label = QLabel()
        arrow_label.setPixmap(qta.icon("fa5s.chevron-right", color="#bdc3c7").pixmap(16, 16))
        arrow_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(icon_label)
        layout.addLayout(content_layout)
        layout.addWidget(arrow_label)
        
    def mousePressEvent(self, event):
        """Emite señal al hacer clic."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
        
    def enterEvent(self, event):
        """Efecto hover al entrar."""
        self.setStyleSheet(f"""
            QFrame#QuickActionCard {{
                background-color: {self.color}15;
                border: 1px solid {self.color}40;
            }}
        """)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Restaura estilo al salir."""
        self.setStyleSheet("")
        super().leaveEvent(event)