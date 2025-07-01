"""
URLs para la aplicación workouts de Fit_Control.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Crear router para ViewSets
router = DefaultRouter()
router.register(r'exercises', views.ExerciseViewSet)
router.register(r'plans', views.WorkoutPlanViewSet, basename='workoutplan')
router.register(r'log', views.UserPerformanceLogViewSet, basename='userperformancelog')
router.register(r'progress', views.UserProgressView, basename='userprogress')

app_name = 'workouts'

urlpatterns = [
    # Incluir todas las rutas del router
    path('', include(router.urls)),
    
    # URLs adicionales si las necesitamos
    # path('exercises/analytics/', views.exercises_analytics, name='exercises-analytics'),
]