"""
Configuración del admin de Django para la app analysis.
"""

from django.contrib import admin
from .models import VideoAnalysis, ExerciseAnalysisConfig, AnalysisMetrics


@admin.register(VideoAnalysis)
class VideoAnalysisAdmin(admin.ModelAdmin):
    """Admin para el modelo VideoAnalysis."""
    
    list_display = ['id', 'user', 'exercise', 'status', 'rep_count', 'feedback_score', 'created_at']
    list_filter = ['status', 'exercise__muscle_group', 'created_at']
    search_fields = ['user__username', 'exercise__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'processing_time']
    
    fieldsets = (
        ('Información básica', {
            'fields': ('user', 'exercise', 'status')
        }),
        ('Archivos', {
            'fields': ('video_file', 'processed_video')
        }),
        ('Resultados', {
            'fields': ('rep_count', 'feedback_score', 'feedback_text'),
            'classes': ('collapse',)
        }),
        ('Datos técnicos', {
            'fields': ('analysis_data', 'processing_time', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'exercise')


class AnalysisMetricsInline(admin.TabularInline):
    """Inline para métricas dentro de un VideoAnalysis."""
    
    model = AnalysisMetrics
    extra = 0
    fields = ['rep_number', 'duration', 'rom_score', 'speed_score', 'form_score', 'symmetry_score']
    readonly_fields = ['rep_number', 'duration', 'rom_score', 'speed_score', 'form_score', 'symmetry_score']


@admin.register(AnalysisMetrics)
class AnalysisMetricsAdmin(admin.ModelAdmin):
    """Admin para el modelo AnalysisMetrics."""
    
    list_display = ['video_analysis', 'rep_number', 'duration', 'rom_score', 'speed_score', 'form_score']
    list_filter = ['video_analysis__exercise__muscle_group']
    search_fields = ['video_analysis__user__username', 'video_analysis__exercise__name']
    ordering = ['video_analysis', 'rep_number']
    
    fieldsets = (
        ('Información básica', {
            'fields': ('video_analysis', 'rep_number', 'duration')
        }),
        ('Puntuaciones', {
            'fields': ('rom_score', 'speed_score', 'form_score', 'symmetry_score')
        }),
        ('Datos detallados', {
            'fields': ('detected_errors', 'landmark_data'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'video_analysis__user', 'video_analysis__exercise'
        )


@admin.register(ExerciseAnalysisConfig)
class ExerciseAnalysisConfigAdmin(admin.ModelAdmin):
    """Admin para el modelo ExerciseAnalysisConfig."""
    
    list_display = ['exercise', 'rep_detection_threshold', 'min_frames_per_rep', 'is_active', 'updated_at']
    list_filter = ['is_active', 'exercise__muscle_group', 'updated_at']
    search_fields = ['exercise__name']
    ordering = ['exercise__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Ejercicio', {
            'fields': ('exercise', 'is_active')
        }),
        ('Configuración de detección', {
            'fields': ('rep_detection_threshold', 'min_frames_per_rep')
        }),
        ('Landmarks y ángulos', {
            'fields': ('key_landmarks', 'angle_ranges'),
            'classes': ('collapse',)
        }),
        ('Patrones y errores', {
            'fields': ('movement_patterns', 'common_errors'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('exercise')


# Personalizar el admin para mejorar la visualización de VideoAnalysis
class VideoAnalysisAdminImproved(VideoAnalysisAdmin):
    """Versión mejorada del admin para VideoAnalysis con métricas inline."""
    
    inlines = [AnalysisMetricsInline]
    
    def get_inline_instances(self, request, obj=None):
        """Solo mostrar métricas si el análisis está completado."""
        if obj and obj.status == 'completed':
            return super().get_inline_instances(request, obj)
        return []

# Re-registrar con la versión mejorada
admin.site.unregister(VideoAnalysis)
admin.site.register(VideoAnalysis, VideoAnalysisAdminImproved)
