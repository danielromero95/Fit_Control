"""
Modelos para la aplicación analysis de Fit_Control.

Esta aplicación gestiona el análisis de vídeo con IA para evaluar 
la técnica de los ejercicios.
"""

from django.db import models
from django.contrib.auth.models import User
from workouts.models import Exercise


class VideoAnalysis(models.Model):
    """
    Almacena el resultado del análisis de un vídeo de ejercicio.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='video_analyses',
        help_text="Usuario que subió el vídeo"
    )
    
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='video_analyses',
        help_text="Ejercicio que se está analizando"
    )
    
    video_file = models.FileField(
        upload_to='analysis_videos/%Y/%m/%d/',
        help_text="Archivo de vídeo original"
    )
    
    processed_video = models.FileField(
        upload_to='processed_videos/%Y/%m/%d/',
        null=True,
        blank=True,
        help_text="Vídeo procesado con anotaciones"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Estado del análisis"
    )
    
    rep_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Número de repeticiones detectadas"
    )
    
    feedback_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Puntuación general de la técnica (0.0 a 1.0)"
    )
    
    feedback_text = models.TextField(
        blank=True,
        help_text="Feedback detallado generado por la IA"
    )
    
    analysis_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Datos detallados del análisis (landmarks, ángulos, etc.)"
    )
    
    processing_time = models.FloatField(
        null=True,
        blank=True,
        help_text="Tiempo de procesamiento en segundos"
    )
    
    error_message = models.TextField(
        blank=True,
        help_text="Mensaje de error si el análisis falló"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Análisis de Vídeo"
        verbose_name_plural = "Análisis de Vídeos"
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['exercise', 'status']),
        ]
    
    def __str__(self):
        return f"Análisis {self.id} - {self.exercise.name} ({self.status})"


class ExerciseAnalysisConfig(models.Model):
    """
    Configuración específica para el análisis de cada tipo de ejercicio.
    """
    
    exercise = models.OneToOneField(
        Exercise,
        on_delete=models.CASCADE,
        related_name='analysis_config',
        help_text="Ejercicio al que se aplica esta configuración"
    )
    
    key_landmarks = models.JSONField(
        help_text="Landmarks clave para este ejercicio (ej. codos, rodillas)"
    )
    
    angle_ranges = models.JSONField(
        help_text="Rangos de ángulos óptimos para cada articulación"
    )
    
    movement_patterns = models.JSONField(
        help_text="Patrones de movimiento esperados"
    )
    
    common_errors = models.JSONField(
        help_text="Errores comunes y sus indicadores"
    )
    
    min_frames_per_rep = models.PositiveIntegerField(
        default=30,
        help_text="Mínimo número de frames por repetición"
    )
    
    rep_detection_threshold = models.FloatField(
        default=0.7,
        help_text="Umbral para detectar una repetición completa"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Si esta configuración está activa"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración de Análisis"
        verbose_name_plural = "Configuraciones de Análisis"
    
    def __str__(self):
        return f"Config: {self.exercise.name}"


class AnalysisMetrics(models.Model):
    """
    Métricas específicas extraídas del análisis de un vídeo.
    """
    
    video_analysis = models.ForeignKey(
        VideoAnalysis,
        on_delete=models.CASCADE,
        related_name='metrics',
        help_text="Análisis al que pertenecen estas métricas"
    )
    
    rep_number = models.PositiveIntegerField(
        help_text="Número de la repetición"
    )
    
    duration = models.FloatField(
        help_text="Duración de la repetición en segundos"
    )
    
    rom_score = models.FloatField(
        help_text="Puntuación del rango de movimiento (0.0 a 1.0)"
    )
    
    speed_score = models.FloatField(
        help_text="Puntuación de la velocidad del movimiento (0.0 a 1.0)"
    )
    
    form_score = models.FloatField(
        help_text="Puntuación de la forma/técnica (0.0 a 1.0)"
    )
    
    symmetry_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Puntuación de simetría (0.0 a 1.0)"
    )
    
    detected_errors = models.JSONField(
        null=True,
        blank=True,
        help_text="Errores detectados en esta repetición"
    )
    
    landmark_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Datos de landmarks para esta repetición"
    )
    
    class Meta:
        unique_together = ['video_analysis', 'rep_number']
        ordering = ['video_analysis', 'rep_number']
        verbose_name = "Métrica de Análisis"
        verbose_name_plural = "Métricas de Análisis"
    
    def __str__(self):
        return f"Rep {self.rep_number} - Análisis {self.video_analysis.id}"
