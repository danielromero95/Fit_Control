"""
Configuración del admin de Django para la app workouts.
"""

from django.contrib import admin
from .models import (
    Exercise,
    WorkoutPlan,
    WorkoutDay,
    WorkoutExercise,
    UserPerformanceLog,
    UserWorkoutPlan
)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    """Admin para el modelo Exercise."""
    
    list_display = ['name', 'muscle_group', 'difficulty', 'created_at']
    list_filter = ['muscle_group', 'difficulty', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'description', 'muscle_group', 'difficulty')
        }),
        ('Recursos', {
            'fields': ('video_url',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class WorkoutExerciseInline(admin.TabularInline):
    """Inline para ejercicios dentro de un WorkoutDay."""
    
    model = WorkoutExercise
    extra = 1
    fields = ['exercise', 'sets', 'reps', 'rest_period', 'order', 'notes']
    ordering = ['order']


@admin.register(WorkoutDay)
class WorkoutDayAdmin(admin.ModelAdmin):
    """Admin para el modelo WorkoutDay."""
    
    list_display = ['plan', 'day_of_week', 'name']
    list_filter = ['day_of_week', 'plan']
    search_fields = ['plan__name', 'name']
    inlines = [WorkoutExerciseInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('plan')


class WorkoutDayInline(admin.StackedInline):
    """Inline para días dentro de un WorkoutPlan."""
    
    model = WorkoutDay
    extra = 0
    fields = ['day_of_week', 'name']
    show_change_link = True


@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    """Admin para el modelo WorkoutPlan."""
    
    list_display = ['name', 'creator', 'is_public', 'created_at', 'followers_count']
    list_filter = ['is_public', 'created_at', 'creator']
    search_fields = ['name', 'description', 'creator__username']
    readonly_fields = ['created_at', 'updated_at', 'followers_count']
    inlines = [WorkoutDayInline]
    
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'description', 'creator', 'is_public')
        }),
        ('Estadísticas', {
            'fields': ('followers_count',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def followers_count(self, obj):
        """Mostrar número de seguidores del plan."""
        return obj.followers.filter(is_active=True).count()
    followers_count.short_description = 'Seguidores activos'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('creator')


@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    """Admin para el modelo WorkoutExercise."""
    
    list_display = ['exercise', 'workout_day', 'sets', 'reps', 'rest_period', 'order']
    list_filter = ['workout_day__plan', 'exercise__muscle_group']
    search_fields = ['exercise__name', 'workout_day__plan__name']
    ordering = ['workout_day__plan', 'workout_day__day_of_week', 'order']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'exercise', 'workout_day__plan'
        )


@admin.register(UserPerformanceLog)
class UserPerformanceLogAdmin(admin.ModelAdmin):
    """Admin para el modelo UserPerformanceLog."""
    
    list_display = ['user', 'exercise_name', 'date', 'set_number', 'weight', 'reps_completed', 'feedback_score']
    list_filter = ['date', 'workout_exercise__exercise__muscle_group']
    search_fields = ['user__username', 'workout_exercise__exercise__name']
    ordering = ['-date', '-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Usuario y ejercicio', {
            'fields': ('user', 'workout_exercise', 'date')
        }),
        ('Rendimiento', {
            'fields': ('weight', 'reps_completed', 'set_number')
        }),
        ('Análisis de vídeo', {
            'fields': ('feedback_score', 'feedback_text', 'video_file'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def exercise_name(self, obj):
        """Mostrar nombre del ejercicio."""
        return obj.workout_exercise.exercise.name
    exercise_name.short_description = 'Ejercicio'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'workout_exercise__exercise'
        )


@admin.register(UserWorkoutPlan)
class UserWorkoutPlanAdmin(admin.ModelAdmin):
    """Admin para el modelo UserWorkoutPlan."""
    
    list_display = ['user', 'workout_plan', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'start_date', 'workout_plan']
    search_fields = ['user__username', 'workout_plan__name']
    ordering = ['-start_date']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'workout_plan')
