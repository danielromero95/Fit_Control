"""
Modelos para la aplicación workouts de Fit_Control.

Esta aplicación gestiona ejercicios, planes de entrenamiento y el registro 
de rendimiento de los usuarios.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Exercise(models.Model):
    """
    Representa un ejercicio individual que puede ser realizado.
    """
    
    MUSCLE_GROUP_CHOICES = [
        ('pecho', 'Pecho'),
        ('espalda', 'Espalda'),
        ('hombros', 'Hombros'),
        ('biceps', 'Bíceps'),
        ('triceps', 'Tríceps'),
        ('piernas', 'Piernas'),
        ('cuadriceps', 'Cuádriceps'),
        ('isquiotibiales', 'Isquiotibiales'),
        ('gluteos', 'Glúteos'),
        ('pantorrillas', 'Pantorrillas'),
        ('abdominales', 'Abdominales'),
        ('cardio', 'Cardio'),
        ('cuerpo_completo', 'Cuerpo Completo'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('principiante', 'Principiante'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
    ]
    
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Nombre del ejercicio (ej. Press de Banca)"
    )
    
    description = models.TextField(
        help_text="Descripción detallada de la técnica del ejercicio"
    )
    
    muscle_group = models.CharField(
        max_length=50,
        choices=MUSCLE_GROUP_CHOICES,
        help_text="Grupo muscular principal trabajado"
    )
    
    video_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL a un vídeo de demostración del ejercicio"
    )
    
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='intermedio',
        help_text="Nivel de dificultad del ejercicio"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Ejercicio"
        verbose_name_plural = "Ejercicios"
    
    def __str__(self):
        return f"{self.name} ({self.get_muscle_group_display()})"


class WorkoutPlan(models.Model):
    """
    Representa un plan de entrenamiento completo.
    """
    
    name = models.CharField(
        max_length=255,
        help_text="Nombre del plan (ej. Hipertrofia 3 días/semana)"
    )
    
    description = models.TextField(
        help_text="Descripción detallada del plan de entrenamiento"
    )
    
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_plans',
        help_text="Usuario o admin que creó el plan"
    )
    
    is_public = models.BooleanField(
        default=True,
        help_text="Si el plan está disponible para todos los usuarios"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Plan de Entrenamiento"
        verbose_name_plural = "Planes de Entrenamiento"
    
    def __str__(self):
        return f"{self.name} (por {self.creator.username})"


class WorkoutDay(models.Model):
    """
    Representa un día específico dentro de un plan de entrenamiento.
    """
    
    DAY_CHOICES = [
        (1, 'Lunes'),
        (2, 'Martes'),
        (3, 'Miércoles'),
        (4, 'Jueves'),
        (5, 'Viernes'),
        (6, 'Sábado'),
        (7, 'Domingo'),
    ]
    
    plan = models.ForeignKey(
        WorkoutPlan,
        on_delete=models.CASCADE,
        related_name='workout_days',
        help_text="Plan al que pertenece este día"
    )
    
    day_of_week = models.IntegerField(
        choices=DAY_CHOICES,
        help_text="Día de la semana (1=Lunes, 7=Domingo)"
    )
    
    name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Nombre opcional para el día (ej. 'Día de Pecho')"
    )
    
    exercises = models.ManyToManyField(
        Exercise,
        through='WorkoutExercise',
        related_name='workout_days',
        help_text="Ejercicios programados para este día"
    )
    
    class Meta:
        unique_together = ['plan', 'day_of_week']
        ordering = ['plan', 'day_of_week']
        verbose_name = "Día de Entrenamiento"
        verbose_name_plural = "Días de Entrenamiento"
    
    def __str__(self):
        return f"{self.plan.name} - {self.get_day_of_week_display()}"


class WorkoutExercise(models.Model):
    """
    Tabla intermedia que define los ejercicios específicos de un día de entrenamiento
    con sus series, repeticiones y tiempo de descanso.
    """
    
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        help_text="Ejercicio a realizar"
    )
    
    workout_day = models.ForeignKey(
        WorkoutDay,
        on_delete=models.CASCADE,
        related_name='workout_exercises',
        help_text="Día de entrenamiento"
    )
    
    sets = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Número de series"
    )
    
    reps = models.CharField(
        max_length=20,
        help_text="Rango de repeticiones (ej. '8-12' o '15')"
    )
    
    rest_period = models.PositiveIntegerField(
        help_text="Tiempo de descanso en segundos",
        validators=[MinValueValidator(30), MaxValueValidator(600)]
    )
    
    order = models.PositiveIntegerField(
        default=1,
        help_text="Orden del ejercicio en el día"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Notas adicionales sobre el ejercicio"
    )
    
    class Meta:
        unique_together = ['exercise', 'workout_day']
        ordering = ['workout_day', 'order']
        verbose_name = "Ejercicio de Entrenamiento"
        verbose_name_plural = "Ejercicios de Entrenamiento"
    
    def __str__(self):
        return f"{self.exercise.name}: {self.sets}x{self.reps}"


class UserPerformanceLog(models.Model):
    """
    Registra el rendimiento de un usuario en un ejercicio específico.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='performance_logs',
        help_text="Usuario que realizó el ejercicio"
    )
    
    workout_exercise = models.ForeignKey(
        WorkoutExercise,
        on_delete=models.CASCADE,
        related_name='performance_logs',
        help_text="Ejercicio específico del plan"
    )
    
    date = models.DateField(
        help_text="Fecha de la sesión"
    )
    
    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Peso levantado en kilogramos"
    )
    
    reps_completed = models.PositiveIntegerField(
        help_text="Repeticiones completadas en esta serie"
    )
    
    set_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Número de la serie"
    )
    
    feedback_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Puntuación del análisis de vídeo (0.0 a 1.0)"
    )
    
    feedback_text = models.TextField(
        blank=True,
        help_text="Comentarios generados por la IA sobre la técnica"
    )
    
    video_file = models.FileField(
        upload_to='user_videos/',
        null=True,
        blank=True,
        help_text="Archivo de vídeo del ejercicio realizado"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Registro de Rendimiento"
        verbose_name_plural = "Registros de Rendimiento"
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['workout_exercise', 'date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.workout_exercise.exercise.name} - {self.date}"


class UserWorkoutPlan(models.Model):
    """
    Asocia un usuario con un plan de entrenamiento que está siguiendo.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='current_plans'
    )
    
    workout_plan = models.ForeignKey(
        WorkoutPlan,
        on_delete=models.CASCADE,
        related_name='followers'
    )
    
    start_date = models.DateField(
        help_text="Fecha en que el usuario comenzó este plan"
    )
    
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha en que el usuario terminó/abandonó el plan"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Si el usuario está siguiendo actualmente este plan"
    )
    
    class Meta:
        unique_together = ['user', 'workout_plan', 'start_date']
        ordering = ['-start_date']
        verbose_name = "Plan de Usuario"
        verbose_name_plural = "Planes de Usuario"
    
    def __str__(self):
        status = "Activo" if self.is_active else "Inactivo"
        return f"{self.user.username} - {self.workout_plan.name} ({status})"
