from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QScrollArea,
    QFrame,
    QLabel,
    QSplitter
)
from PyQt5.QtCore import QDate, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QFont
import qtawesome as qta

from src.gui.widgets.custom_calendar_widget import CustomCalendarWidget
from src.gui.widgets.daily_plan_card import DailyPlanCard
from src.gui.widgets.kpi_card_widget import KPICardWidget, ProgressCardWidget, QuickActionWidget
from src import database


class EnhancedDashboardPage(QWidget):
    """Página de dashboard mejorada con métricas en tiempo real y widgets modernos."""

    exercise_selected = pyqtSignal(str)
    page_requested = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Timer para actualizar métricas cada 30 segundos
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_metrics)
        self.update_timer.start(30000)  # 30 segundos

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Configura la interfaz de usuario del dashboard mejorado."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header con bienvenida
        header = self._create_header()
        main_layout.addWidget(header)

        # Contenido principal con scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameStyle(QFrame.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # KPI Cards Grid
        kpi_section = self._create_kpi_section()
        content_layout.addWidget(kpi_section)

        # Splitter para calendario y plan diario
        splitter = QSplitter(Qt.Horizontal)
        
        # Lado izquierdo - Calendario y progreso
        left_widget = self._create_left_panel()
        splitter.addWidget(left_widget)

        # Lado derecho - Plan diario y acciones rápidas
        right_widget = self._create_right_panel()
        splitter.addWidget(right_widget)

        splitter.setSizes([400, 300])
        content_layout.addWidget(splitter)

        # Sección de objetivos semanales
        goals_section = self._create_goals_section()
        content_layout.addWidget(goals_section)

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def _create_header(self) -> QWidget:
        """Crea el header con saludo personalizado."""
        header = QFrame()
        header.setObjectName("DashboardHeader")
        header.setStyleSheet("""
            QFrame#DashboardHeader {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 12px;
                margin: 10px;
            }
        """)
        header.setFixedHeight(100)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 20, 30, 20)

        # Información del usuario
        user_info = QVBoxLayout()
        
        greeting = QLabel("¡Bienvenido de vuelta!")
        greeting.setFont(QFont("Segoe UI", 14, QFont.Bold))
        greeting.setStyleSheet("color: white; background: transparent;")
        
        user_name = QLabel("Entrenador")
        user_name.setFont(QFont("Segoe UI", 20, QFont.Bold))
        user_name.setStyleSheet("color: white; background: transparent;")
        
        user_info.addWidget(greeting)
        user_info.addWidget(user_name)
        
        # Estadística rápida
        quick_stat = QVBoxLayout()
        
        stat_label = QLabel("Racha Actual")
        stat_label.setFont(QFont("Segoe UI", 10))
        stat_label.setStyleSheet("color: rgba(255,255,255,0.8); background: transparent;")
        stat_label.setAlignment(Qt.AlignRight)
        
        stat_value = QLabel("7 días")
        stat_value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        stat_value.setStyleSheet("color: white; background: transparent;")
        stat_value.setAlignment(Qt.AlignRight)
        
        quick_stat.addWidget(stat_label)
        quick_stat.addWidget(stat_value)
        
        layout.addLayout(user_info)
        layout.addStretch()
        layout.addLayout(quick_stat)

        return header

    def _create_kpi_section(self) -> QWidget:
        """Crea la sección de KPIs con métricas principales."""
        section = QFrame()
        section.setObjectName("KPISection")
        
        layout = QVBoxLayout(section)
        layout.setSpacing(15)

        # Título de sección
        title = QLabel("Resumen de Actividad")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        # Grid de KPIs
        grid = QGridLayout()
        grid.setSpacing(15)

        # KPIs principales
        self.workouts_kpi = KPICardWidget(
            "Entrenamientos",
            "12",
            "fa5s.dumbbell",
            "+3 esta semana",
            True,
            "#3498db"
        )
        self.workouts_kpi.clicked.connect(lambda: self.page_requested.emit("progress"))

        self.reps_kpi = KPICardWidget(
            "Repeticiones",
            "450",
            "fa5s.redo-alt",
            "+15% vs anterior",
            True,
            "#e74c3c"
        )

        self.time_kpi = KPICardWidget(
            "Tiempo Total",
            "8.5h",
            "fa5s.clock",
            "Esta semana",
            True,
            "#f39c12"
        )

        self.weight_kpi = KPICardWidget(
            "Peso Levantado",
            "2.4t",
            "fa5s.weight-hanging",
            "+200kg esta semana",
            True,
            "#27ae60"
        )

        grid.addWidget(self.workouts_kpi, 0, 0)
        grid.addWidget(self.reps_kpi, 0, 1)
        grid.addWidget(self.time_kpi, 0, 2)
        grid.addWidget(self.weight_kpi, 0, 3)

        layout.addLayout(grid)
        return section

    def _create_left_panel(self) -> QWidget:
        """Crea el panel izquierdo con calendario y progreso."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Calendario
        cal_frame = QFrame()
        cal_frame.setObjectName("CalendarFrame")
        cal_layout = QVBoxLayout(cal_frame)
        
        cal_title = QLabel("Calendario de Entrenamientos")
        cal_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        cal_title.setObjectName("SectionTitle")
        cal_layout.addWidget(cal_title)

        self.calendar = CustomCalendarWidget()
        self.calendar.date_selected.connect(self._on_date_selected)
        cal_layout.addWidget(self.calendar)

        # Progreso semanal
        progress_frame = QFrame()
        progress_frame.setObjectName("ProgressFrame")
        progress_layout = QVBoxLayout(progress_frame)
        
        progress_title = QLabel("Progreso Semanal")
        progress_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        progress_title.setObjectName("SectionTitle")
        progress_layout.addWidget(progress_title)

        self.weekly_progress = ProgressCardWidget(
            "Entrenamientos Completados",
            4, 5, "entrenamientos",
            "#3498db"
        )
        progress_layout.addWidget(self.weekly_progress)

        self.volume_progress = ProgressCardWidget(
            "Volumen de Entrenamiento",
            850, 1000, "kg",
            "#e74c3c"
        )
        progress_layout.addWidget(self.volume_progress)

        layout.addWidget(cal_frame)
        layout.addWidget(progress_frame)

        return widget

    def _create_right_panel(self) -> QWidget:
        """Crea el panel derecho con plan diario y acciones rápidas."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Plan diario
        plan_frame = QFrame()
        plan_frame.setObjectName("PlanFrame")
        plan_layout = QVBoxLayout(plan_frame)
        
        plan_title = QLabel("Plan de Hoy")
        plan_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        plan_title.setObjectName("SectionTitle")
        plan_layout.addWidget(plan_title)

        self.daily_plan_card = DailyPlanCard()
        self.daily_plan_card.exercise_clicked.connect(self.exercise_selected)
        plan_layout.addWidget(self.daily_plan_card)

        # Acciones rápidas
        actions_frame = QFrame()
        actions_frame.setObjectName("ActionsFrame")
        actions_layout = QVBoxLayout(actions_frame)
        
        actions_title = QLabel("Acciones Rápidas")
        actions_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        actions_title.setObjectName("SectionTitle")
        actions_layout.addWidget(actions_title)

        # Crear acciones rápidas
        new_workout_action = QuickActionWidget(
            "Nuevo Entrenamiento",
            "Iniciar un entrenamiento personalizado",
            "fa5s.play",
            "#27ae60"
        )
        new_workout_action.clicked.connect(lambda: self.page_requested.emit("exercises"))

        analyze_action = QuickActionWidget(
            "Analizar Vídeo",
            "Subir y analizar técnica de ejercicio",
            "fa5s.video",
            "#3498db"
        )
        analyze_action.clicked.connect(lambda: self.page_requested.emit("analysis"))

        progress_action = QuickActionWidget(
            "Ver Progreso",
            "Revisar historial y estadísticas",
            "fa5s.chart-line",
            "#f39c12"
        )
        progress_action.clicked.connect(lambda: self.page_requested.emit("progress"))

        actions_layout.addWidget(new_workout_action)
        actions_layout.addWidget(analyze_action)
        actions_layout.addWidget(progress_action)

        layout.addWidget(plan_frame)
        layout.addWidget(actions_frame)

        return widget

    def _create_goals_section(self) -> QWidget:
        """Crea la sección de objetivos y metas."""
        section = QFrame()
        section.setObjectName("GoalsSection")
        
        layout = QVBoxLayout(section)
        layout.setSpacing(15)

        # Título
        title = QLabel("Objetivos de la Semana")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        # Grid de objetivos
        goals_grid = QGridLayout()
        goals_grid.setSpacing(15)

        # Objetivos específicos
        strength_goal = ProgressCardWidget(
            "Incremento de Fuerza",
            75, 100, "%",
            "#e74c3c"
        )

        cardio_goal = ProgressCardWidget(
            "Resistencia Cardiovascular",
            3, 4, "sesiones",
            "#3498db"
        )

        consistency_goal = ProgressCardWidget(
            "Consistencia Semanal",
            5, 6, "días",
            "#27ae60"
        )

        goals_grid.addWidget(strength_goal, 0, 0)
        goals_grid.addWidget(cardio_goal, 0, 1)
        goals_grid.addWidget(consistency_goal, 0, 2)

        layout.addLayout(goals_grid)
        return section

    def _load_data(self):
        """Carga los datos iniciales del dashboard."""
        self._plan_data = self._load_active_plan()
        self._on_date_selected(QDate.currentDate())
        self.update_metrics()

    def _parse_plan_md(self, plan_md: str) -> dict[str, list[tuple[str, str]]]:
        """Convierte Markdown en un diccionario de plan semanal."""
        plan: dict[str, list[tuple[str, str]]] = {}
        current_day: str | None = None
        for line in plan_md.splitlines():
            if line.startswith("### "):
                current_day = line[4:].strip()
                plan[current_day] = []
                continue
            if current_day is None or not line.strip():
                continue
            if line.strip().lower().startswith("descanso"):
                plan[current_day] = []
                continue
            if line.startswith("- "):
                text = line[2:].strip()
                parts = text.rsplit(" ", 1)
                if len(parts) == 2:
                    plan[current_day].append((parts[0], parts[1]))
                else:
                    plan[current_day].append((text, ""))
        return plan

    def _load_active_plan(self) -> dict[str, list[tuple[str, str]]]:
        """Carga el plan activo desde la base de datos."""
        plan_id = database.get_active_plan_id()
        if plan_id is not None:
            row = database.get_plan_by_id(plan_id)
            if row and row.get("plan_content_md"):
                return self._parse_plan_md(row["plan_content_md"])
        return self._parse_plan_md("")

    def _on_date_selected(self, date: QDate) -> None:
        """Maneja la selección de fecha en el calendario."""
        day_names = {
            1: "Lunes", 2: "Martes", 3: "Miércoles",
            4: "Jueves", 5: "Viernes", 6: "Sábado", 7: "Domingo"
        }
        day_es = day_names.get(date.dayOfWeek(), "")
        exercises = self._plan_data.get(day_es, [])
        self.daily_plan_card.update_plan(exercises)

    def update_metrics(self):
        """Actualiza las métricas del dashboard."""
        try:
            # Obtener datos reales de la base de datos
            total_workouts = database.get_total_workouts_count()
            total_reps = database.get_total_repetitions_count()
            total_time = database.get_total_workout_time()
            total_weight = database.get_total_weight_lifted()

            # Actualizar KPIs
            if hasattr(self, 'workouts_kpi'):
                self.workouts_kpi.update_value(
                    str(total_workouts or 12),
                    "+3 esta semana",
                    True
                )

            if hasattr(self, 'reps_kpi'):
                self.reps_kpi.update_value(
                    str(total_reps or 450),
                    "+15% vs anterior",
                    True
                )

            # Actualizar progreso semanal
            if hasattr(self, 'weekly_progress'):
                current_week_workouts = database.get_current_week_workouts()
                self.weekly_progress.update_progress(current_week_workouts or 4, 5)

        except Exception as e:
            print(f"Error actualizando métricas: {e}")

    def refresh_dashboard(self) -> None:
        """Refresca todos los datos del dashboard."""
        self._load_data()
        self.update_metrics()

    def showEvent(self, event):
        """Actualiza datos cuando se muestra la página."""
        super().showEvent(event)
        self.refresh_dashboard()