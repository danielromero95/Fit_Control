"""
URLs para la aplicación analysis de Fit_Control.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Crear router para ViewSets
router = DefaultRouter()
router.register(r'history', views.VideoAnalysisViewSet, basename='videoanalysis')

app_name = 'analysis'

urlpatterns = [
    # Endpoint principal para análisis de vídeo
    path('analyze/', views.analyze_video, name='analyze-video'),
    
    # Endpoints para gestionar análisis
    path('analyze/<int:analysis_id>/status/', views.analysis_status, name='analysis-status'),
    path('analyze/<int:analysis_id>/details/', views.analysis_details, name='analysis-details'),
    path('analyze/history/', views.user_analyses, name='user-analyses'),
    
    # Incluir rutas del router
    path('', include(router.urls)),
]