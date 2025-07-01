"""
Configuración del admin de Django para la app authentication.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, UserPreferences, UserStats


class UserProfileInline(admin.StackedInline):
    """Inline para el perfil de usuario."""
    
    model = UserProfile
    can_delete = False
    verbose_name = 'Perfil'
    verbose_name_plural = 'Perfiles'
    
    fieldsets = (
        ('Información personal', {
            'fields': ('date_of_birth', 'gender', 'phone_number')
        }),
        ('Información física', {
            'fields': ('height', 'weight')
        }),
        ('Fitness', {
            'fields': ('experience_level', 'primary_goal')
        }),
        ('Configuración', {
            'fields': ('preferred_units', 'enable_notifications', 'enable_video_analysis'),
            'classes': ('collapse',)
        }),
    )


class UserPreferencesInline(admin.StackedInline):
    """Inline para las preferencias del usuario."""
    
    model = UserPreferences
    can_delete = False
    verbose_name = 'Preferencias'
    verbose_name_plural = 'Preferencias'
    
    fieldsets = (
        ('Entrenamiento', {
            'fields': ('preferred_workout_duration', 'preferred_rest_time', 'preferred_workout_time')
        }),
        ('Preferencias específicas', {
            'fields': ('preferred_muscle_groups', 'avoided_exercises', 'available_days'),
            'classes': ('collapse',)
        }),
        ('Análisis', {
            'fields': ('analysis_sensitivity', 'auto_save_videos'),
            'classes': ('collapse',)
        }),
    )


class UserStatsInline(admin.StackedInline):
    """Inline para las estadísticas del usuario."""
    
    model = UserStats
    can_delete = False
    verbose_name = 'Estadísticas'
    verbose_name_plural = 'Estadísticas'
    readonly_fields = [
        'total_workouts', 'total_exercises', 'total_sets', 'total_reps',
        'total_workout_time', 'average_workout_duration', 'total_videos_analyzed',
        'average_technique_score', 'current_streak', 'longest_streak', 'last_workout_date'
    ]
    
    fieldsets = (
        ('Actividad', {
            'fields': ('total_workouts', 'total_exercises', 'total_sets', 'total_reps')
        }),
        ('Tiempo', {
            'fields': ('total_workout_time', 'average_workout_duration')
        }),
        ('Análisis', {
            'fields': ('total_videos_analyzed', 'average_technique_score')
        }),
        ('Racha', {
            'fields': ('current_streak', 'longest_streak', 'last_workout_date')
        }),
    )


class UserAdmin(BaseUserAdmin):
    """Admin extendido para el modelo User."""
    
    inlines = (UserProfileInline, UserPreferencesInline, UserStatsInline)
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin para el modelo UserProfile."""
    
    list_display = ['user', 'age', 'height', 'weight', 'bmi', 'experience_level', 'primary_goal']
    list_filter = ['gender', 'experience_level', 'primary_goal', 'preferred_units']
    search_fields = ['user__username', 'user__email', 'phone_number']
    ordering = ['user__username']
    readonly_fields = ['age', 'bmi', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Información personal', {
            'fields': ('date_of_birth', 'age', 'gender', 'phone_number')
        }),
        ('Información física', {
            'fields': ('height', 'weight', 'bmi')
        }),
        ('Fitness', {
            'fields': ('experience_level', 'primary_goal')
        }),
        ('Configuración', {
            'fields': ('preferred_units', 'enable_notifications', 'enable_video_analysis')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    """Admin para el modelo UserPreferences."""
    
    list_display = ['user', 'preferred_workout_duration', 'preferred_rest_time', 'analysis_sensitivity']
    list_filter = ['analysis_sensitivity', 'auto_save_videos']
    search_fields = ['user__username']
    ordering = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Entrenamiento', {
            'fields': ('preferred_workout_duration', 'preferred_rest_time', 'preferred_workout_time')
        }),
        ('Disponibilidad', {
            'fields': ('available_days',)
        }),
        ('Preferencias específicas', {
            'fields': ('preferred_muscle_groups', 'avoided_exercises'),
            'classes': ('collapse',)
        }),
        ('Análisis', {
            'fields': ('analysis_sensitivity', 'auto_save_videos')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(UserStats)
class UserStatsAdmin(admin.ModelAdmin):
    """Admin para el modelo UserStats."""
    
    list_display = [
        'user', 'total_workouts', 'total_exercises', 'current_streak', 
        'average_technique_score', 'last_workout_date'
    ]
    list_filter = ['last_workout_date']
    search_fields = ['user__username']
    ordering = ['-total_workouts']
    readonly_fields = [
        'total_workouts', 'total_exercises', 'total_sets', 'total_reps',
        'total_workout_time', 'average_workout_duration', 'total_videos_analyzed',
        'average_technique_score', 'current_streak', 'longest_streak', 'updated_at'
    ]
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Estadísticas de actividad', {
            'fields': ('total_workouts', 'total_exercises', 'total_sets', 'total_reps')
        }),
        ('Estadísticas de tiempo', {
            'fields': ('total_workout_time', 'average_workout_duration')
        }),
        ('Estadísticas de análisis', {
            'fields': ('total_videos_analyzed', 'average_technique_score')
        }),
        ('Racha y consistencia', {
            'fields': ('current_streak', 'longest_streak', 'last_workout_date')
        }),
        ('Metadatos', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Re-registrar el modelo User con nuestro admin personalizado
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
