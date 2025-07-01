"""
Modelos para la aplicación authentication de Fit_Control.

Esta aplicación extiende la funcionalidad de autenticación y 
perfiles de usuario.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class UserProfile(models.Model):
    """
    Perfil extendido del usuario con información de fitness.
    """
    
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
        ('N', 'Prefiero no decir'),
    ]
    
    EXPERIENCE_CHOICES = [
        ('beginner', 'Principiante (0-6 meses)'),
        ('intermediate', 'Intermedio (6 meses - 2 años)'),
        ('advanced', 'Avanzado (2+ años)'),
        ('expert', 'Experto (5+ años)'),
    ]
    
    GOAL_CHOICES = [
        ('weight_loss', 'Pérdida de peso'),
        ('muscle_gain', 'Ganancia muscular'),
        ('strength', 'Aumento de fuerza'),
        ('endurance', 'Resistencia'),
        ('general_fitness', 'Fitness general'),
        ('rehabilitation', 'Rehabilitación'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Información personal
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha de nacimiento"
    )
    
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        help_text="Género"
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Número de teléfono"
    )
    
    # Información física
    height = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(100), MaxValueValidator(250)],
        help_text="Altura en centímetros"
    )
    
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(300)],
        help_text="Peso en kilogramos"
    )
    
    # Información de fitness
    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default='beginner',
        help_text="Nivel de experiencia en el gimnasio"
    )
    
    primary_goal = models.CharField(
        max_length=20,
        choices=GOAL_CHOICES,
        default='general_fitness',
        help_text="Objetivo principal de entrenamiento"
    )
    
    # Configuraciones de la app
    preferred_units = models.CharField(
        max_length=10,
        choices=[('metric', 'Métrico'), ('imperial', 'Imperial')],
        default='metric',
        help_text="Sistema de unidades preferido"
    )
    
    enable_notifications = models.BooleanField(
        default=True,
        help_text="Habilitar notificaciones push"
    )
    
    enable_video_analysis = models.BooleanField(
        default=True,
        help_text="Habilitar análisis automático de vídeo"
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    @property
    def age(self):
        """Calcula la edad del usuario."""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < 
                (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    @property
    def bmi(self):
        """Calcula el BMI del usuario."""
        if self.height and self.weight:
            height_m = self.height / 100
            return float(self.weight) / (height_m ** 2)
        return None


class UserPreferences(models.Model):
    """
    Preferencias específicas del usuario para entrenamientos.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='preferences'
    )
    
    # Preferencias de entrenamiento
    preferred_workout_duration = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(15), MaxValueValidator(180)],
        help_text="Duración preferida del entrenamiento en minutos"
    )
    
    preferred_rest_time = models.PositiveIntegerField(
        default=90,
        validators=[MinValueValidator(30), MaxValueValidator(300)],
        help_text="Tiempo de descanso preferido entre series en segundos"
    )
    
    preferred_muscle_groups = models.JSONField(
        default=list,
        help_text="Grupos musculares de preferencia del usuario"
    )
    
    avoided_exercises = models.JSONField(
        default=list,
        help_text="IDs de ejercicios que el usuario prefiere evitar"
    )
    
    # Disponibilidad
    available_days = models.JSONField(
        default=list,
        help_text="Días de la semana disponibles para entrenar (1-7)"
    )
    
    preferred_workout_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Hora preferida para entrenar"
    )
    
    # Configuraciones de análisis
    analysis_sensitivity = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Baja'),
            ('medium', 'Media'),
            ('high', 'Alta')
        ],
        default='medium',
        help_text="Sensibilidad del análisis de técnica"
    )
    
    auto_save_videos = models.BooleanField(
        default=False,
        help_text="Guardar automáticamente los vídeos analizados"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Preferencias de Usuario"
        verbose_name_plural = "Preferencias de Usuario"
    
    def __str__(self):
        return f"Preferencias de {self.user.username}"


class UserStats(models.Model):
    """
    Estadísticas y métricas del usuario.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='stats'
    )
    
    # Estadísticas de actividad
    total_workouts = models.PositiveIntegerField(default=0)
    total_exercises = models.PositiveIntegerField(default=0)
    total_sets = models.PositiveIntegerField(default=0)
    total_reps = models.PositiveIntegerField(default=0)
    
    # Estadísticas de tiempo
    total_workout_time = models.PositiveIntegerField(
        default=0,
        help_text="Tiempo total de entrenamiento en minutos"
    )
    
    average_workout_duration = models.FloatField(
        default=0.0,
        help_text="Duración promedio de entrenamiento en minutos"
    )
    
    # Estadísticas de análisis
    total_videos_analyzed = models.PositiveIntegerField(default=0)
    average_technique_score = models.FloatField(
        default=0.0,
        help_text="Puntuación promedio de técnica"
    )
    
    # Racha y consistencia
    current_streak = models.PositiveIntegerField(
        default=0,
        help_text="Racha actual de días consecutivos entrenando"
    )
    
    longest_streak = models.PositiveIntegerField(
        default=0,
        help_text="Racha más larga de días consecutivos"
    )
    
    last_workout_date = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha del último entrenamiento"
    )
    
    # Metadatos
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Estadísticas de Usuario"
        verbose_name_plural = "Estadísticas de Usuario"
    
    def __str__(self):
        return f"Stats de {self.user.username}"
