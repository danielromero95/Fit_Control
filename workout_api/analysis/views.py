"""
Views para la aplicación analysis de Fit_Control.

Estas views implementan los endpoints para el análisis de vídeo con IA.
"""

import logging
import os
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
# from celery import current_app  # TODO: Instalar Celery para producción

from workouts.models import Exercise
from .models import VideoAnalysis, ExerciseAnalysisConfig, AnalysisMetrics
from .exercise_analyzer import ExerciseAnalyzer

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def analyze_video(request):
    """
    Endpoint principal para analizar vídeos de ejercicios.
    
    POST /api/analyze/
    
    Parámetros requeridos:
    - user_id: ID del usuario (opcional, se usa el usuario autenticado)
    - exercise_id: ID del ejercicio
    - video: Archivo de vídeo
    
    Respuesta:
    - rep_count: Número de repeticiones detectadas
    - feedback_score: Puntuación de técnica (0.0 a 1.0)
    - feedback_text: Feedback textual detallado
    """
    try:
        # Validar parámetros
        exercise_id = request.data.get('exercise_id')
        video_file = request.FILES.get('video')
        
        if not exercise_id:
            return Response(
                {'error': 'exercise_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not video_file:
            return Response(
                {'error': 'Archivo de vídeo es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que el ejercicio existe
        try:
            exercise = Exercise.objects.get(id=exercise_id)
        except Exercise.DoesNotExist:
            return Response(
                {'error': 'Ejercicio no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validar tipo de archivo
        allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        file_extension = os.path.splitext(video_file.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            return Response(
                {'error': f'Tipo de archivo no soportado. Use: {", ".join(allowed_extensions)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar tamaño de archivo (máximo 100MB por defecto)
        max_size = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 100 * 1024 * 1024)
        if video_file.size > max_size:
            return Response(
                {'error': f'Archivo demasiado grande. Máximo: {max_size // (1024*1024)}MB'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear registro de análisis
        video_analysis = VideoAnalysis.objects.create(
            user=request.user,
            exercise=exercise,
            video_file=video_file,
            status='pending'
        )
        
        logger.info(f"Created video analysis {video_analysis.id} for user {request.user.id}")
        
        # Procesar vídeo sincrónicamente (en producción usar Celery)
        try:
            video_analysis.status = 'processing'
            video_analysis.save()
            
            # Obtener ruta del archivo guardado
            video_path = video_analysis.video_file.path
            
            # Obtener configuración del ejercicio
            config = _get_exercise_config(exercise)
            
            # Analizar vídeo
            analyzer = ExerciseAnalyzer(exercise.id, config)
            results = analyzer.analyze_video(video_path)
            
            if results.get('success', False):
                # Guardar resultados
                video_analysis.status = 'completed'
                video_analysis.rep_count = results.get('rep_count', 0)
                video_analysis.feedback_score = results.get('feedback_score', 0.0)
                video_analysis.feedback_text = results.get('feedback_text', '')
                video_analysis.analysis_data = results.get('analysis_data', {})
                video_analysis.processing_time = results.get('processing_time', 0.0)
                video_analysis.save()
                
                # Guardar métricas detalladas si están disponibles
                _save_analysis_metrics(video_analysis, results.get('analysis_data', {}))
                
                # Respuesta exitosa
                response_data = {
                    'analysis_id': video_analysis.id,
                    'rep_count': video_analysis.rep_count,
                    'feedback_score': video_analysis.feedback_score,
                    'feedback_text': video_analysis.feedback_text,
                    'processing_time': video_analysis.processing_time,
                    'exercise_name': exercise.name,
                    'status': 'completed'
                }
                
                logger.info(f"Analysis {video_analysis.id} completed successfully")
                return Response(response_data, status=status.HTTP_200_OK)
                
            else:
                # Error en el análisis
                video_analysis.status = 'failed'
                video_analysis.error_message = results.get('error', 'Error desconocido en el análisis')
                video_analysis.save()
                
                logger.error(f"Analysis {video_analysis.id} failed: {video_analysis.error_message}")
                return Response(
                    {'error': 'Error procesando el vídeo', 'details': video_analysis.error_message},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            # Error inesperado
            video_analysis.status = 'failed'
            video_analysis.error_message = str(e)
            video_analysis.save()
            
            logger.error(f"Unexpected error in analysis {video_analysis.id}: {str(e)}")
            return Response(
                {'error': 'Error interno del servidor', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Error in analyze_video endpoint: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def analysis_status(request, analysis_id):
    """
    Obtener el estado de un análisis específico.
    
    GET /api/analyze/{analysis_id}/status/
    """
    try:
        video_analysis = get_object_or_404(
            VideoAnalysis,
            id=analysis_id,
            user=request.user
        )
        
        response_data = {
            'analysis_id': video_analysis.id,
            'status': video_analysis.status,
            'created_at': video_analysis.created_at,
            'updated_at': video_analysis.updated_at,
        }
        
        if video_analysis.status == 'completed':
            response_data.update({
                'rep_count': video_analysis.rep_count,
                'feedback_score': video_analysis.feedback_score,
                'feedback_text': video_analysis.feedback_text,
                'processing_time': video_analysis.processing_time,
            })
        elif video_analysis.status == 'failed':
            response_data['error_message'] = video_analysis.error_message
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Error getting analysis status: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_analyses(request):
    """
    Obtener el historial de análisis del usuario.
    
    GET /api/analyze/history/
    """
    try:
        analyses = VideoAnalysis.objects.filter(
            user=request.user
        ).select_related('exercise').order_by('-created_at')
        
        # Paginación simple
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        
        total_count = analyses.count()
        analyses_page = analyses[offset:offset + limit]
        
        results = []
        for analysis in analyses_page:
            result = {
                'id': analysis.id,
                'exercise_id': analysis.exercise.id,
                'exercise_name': analysis.exercise.name,
                'status': analysis.status,
                'created_at': analysis.created_at,
                'updated_at': analysis.updated_at,
            }
            
            if analysis.status == 'completed':
                result.update({
                    'rep_count': analysis.rep_count,
                    'feedback_score': analysis.feedback_score,
                    'processing_time': analysis.processing_time,
                })
            
            results.append(result)
        
        response_data = {
            'count': total_count,
            'results': results,
            'has_next': offset + limit < total_count,
            'has_previous': offset > 0,
        }
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Error getting user analyses: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def analysis_details(request, analysis_id):
    """
    Obtener detalles completos de un análisis.
    
    GET /api/analyze/{analysis_id}/details/
    """
    try:
        video_analysis = get_object_or_404(
            VideoAnalysis,
            id=analysis_id,
            user=request.user
        )
        
        response_data = {
            'id': video_analysis.id,
            'exercise': {
                'id': video_analysis.exercise.id,
                'name': video_analysis.exercise.name,
                'muscle_group': video_analysis.exercise.muscle_group,
                'difficulty': video_analysis.exercise.difficulty,
            },
            'status': video_analysis.status,
            'created_at': video_analysis.created_at,
            'updated_at': video_analysis.updated_at,
        }
        
        if video_analysis.status == 'completed':
            response_data.update({
                'rep_count': video_analysis.rep_count,
                'feedback_score': video_analysis.feedback_score,
                'feedback_text': video_analysis.feedback_text,
                'processing_time': video_analysis.processing_time,
                'analysis_data': video_analysis.analysis_data,
            })
            
            # Incluir métricas detalladas si están disponibles
            metrics = AnalysisMetrics.objects.filter(
                video_analysis=video_analysis
            ).order_by('rep_number')
            
            if metrics.exists():
                response_data['rep_metrics'] = [
                    {
                        'rep_number': metric.rep_number,
                        'duration': metric.duration,
                        'rom_score': metric.rom_score,
                        'speed_score': metric.speed_score,
                        'form_score': metric.form_score,
                        'symmetry_score': metric.symmetry_score,
                        'detected_errors': metric.detected_errors,
                    }
                    for metric in metrics
                ]
        
        elif video_analysis.status == 'failed':
            response_data['error_message'] = video_analysis.error_message
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Error getting analysis details: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Funciones auxiliares

def _get_exercise_config(exercise: Exercise) -> dict:
    """
    Obtener configuración de análisis para un ejercicio específico.
    """
    try:
        config_obj = ExerciseAnalysisConfig.objects.get(
            exercise=exercise,
            is_active=True
        )
        
        return {
            'model_complexity': 1,
            'min_detection_confidence': 0.5,
            'min_tracking_confidence': 0.5,
            'rep_detection_threshold': config_obj.rep_detection_threshold,
            'min_frames_per_rep': config_obj.min_frames_per_rep,
            'key_landmarks': config_obj.key_landmarks,
            'angle_ranges': config_obj.angle_ranges,
            'movement_patterns': config_obj.movement_patterns,
            'common_errors': config_obj.common_errors,
        }
    except ExerciseAnalysisConfig.DoesNotExist:
        # Usar configuración por defecto si no existe configuración específica
        logger.warning(f"No specific config found for exercise {exercise.id}, using defaults")
        return {
            'model_complexity': 1,
            'min_detection_confidence': 0.5,
            'min_tracking_confidence': 0.5,
            'rep_detection_threshold': 0.7,
            'min_frames_per_rep': 30,
        }


def _save_analysis_metrics(video_analysis: VideoAnalysis, analysis_data: dict):
    """
    Guardar métricas detalladas del análisis.
    """
    try:
        repetitions_data = analysis_data.get('repetitions_data', [])
        
        for rep_data in repetitions_data:
            # Simular métricas detalladas (en implementación real, calcular desde datos reales)
            AnalysisMetrics.objects.create(
                video_analysis=video_analysis,
                rep_number=rep_data.get('rep_number', 1),
                duration=rep_data.get('duration_frames', 60) / 30.0,  # Convertir a segundos
                rom_score=0.8,  # Placeholder
                speed_score=0.75,  # Placeholder
                form_score=0.85,  # Placeholder
                symmetry_score=0.9,  # Placeholder
                detected_errors=rep_data.get('detected_errors', []),
                landmark_data=rep_data.get('angles', {}),
            )
        
        logger.info(f"Saved {len(repetitions_data)} rep metrics for analysis {video_analysis.id}")
        
    except Exception as e:
        logger.error(f"Error saving analysis metrics: {str(e)}")


# TODO: Implementar análisis asíncrono con Celery para producción

# @shared_task
# def analyze_video_async(video_analysis_id):
#     """
#     Tarea de Celery para procesar vídeos de forma asíncrona.
#     """
#     try:
#         video_analysis = VideoAnalysis.objects.get(id=video_analysis_id)
#         video_analysis.status = 'processing'
#         video_analysis.save()
#         
#         # Procesar vídeo
#         analyzer = ExerciseAnalyzer(video_analysis.exercise.id)
#         results = analyzer.analyze_video(video_analysis.video_file.path)
#         
#         if results.get('success', False):
#             video_analysis.status = 'completed'
#             video_analysis.rep_count = results.get('rep_count', 0)
#             video_analysis.feedback_score = results.get('feedback_score', 0.0)
#             video_analysis.feedback_text = results.get('feedback_text', '')
#             video_analysis.analysis_data = results.get('analysis_data', {})
#             video_analysis.processing_time = results.get('processing_time', 0.0)
#         else:
#             video_analysis.status = 'failed'
#             video_analysis.error_message = results.get('error', 'Unknown error')
#         
#         video_analysis.save()
#         
#     except Exception as e:
#         video_analysis.status = 'failed'
#         video_analysis.error_message = str(e)
#         video_analysis.save()
#         logger.error(f"Error in async video analysis: {str(e)}")


class VideoAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para acceder al historial de análisis de vídeo.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return VideoAnalysis.objects.filter(
            user=self.request.user
        ).select_related('exercise').order_by('-created_at')
