"""
Views para la aplicación workouts de Fit_Control.

Estas views implementan los endpoints de la API REST para 
gestionar ejercicios, planes y entrenamientos.
"""

from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Max, Count
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    Exercise, 
    WorkoutPlan, 
    WorkoutDay, 
    WorkoutExercise, 
    UserPerformanceLog,
    UserWorkoutPlan
)
from .serializers import (
    ExerciseSerializer,
    WorkoutPlanSerializer,
    WorkoutPlanCreateSerializer,
    WorkoutDaySerializer,
    WorkoutExerciseSerializer,
    UserPerformanceLogSerializer,
    UserWorkoutPlanSerializer,
    UserProgressSerializer,
    ExerciseFilterSerializer
)


class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para gestionar ejercicios.
    
    Endpoints:
    - GET /api/exercises/ - Lista todos los ejercicios
    - GET /api/exercises/{id}/ - Detalle de un ejercicio
    """
    
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['muscle_group', 'difficulty']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'difficulty', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """
        Filtrar ejercicios basado en los parámetros de query.
        """
        queryset = Exercise.objects.all()
        
        # Filtro por grupo muscular
        muscle_group = self.request.query_params.get('muscle_group')
        if muscle_group:
            queryset = queryset.filter(muscle_group=muscle_group)
        
        # Filtro por dificultad
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        return queryset

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """
        Obtener analytics de un ejercicio específico.
        """
        exercise = self.get_object()
        
        # Estadísticas generales del ejercicio
        logs = UserPerformanceLog.objects.filter(
            workout_exercise__exercise=exercise
        )
        
        analytics_data = {
            'exercise_id': exercise.id,
            'exercise_name': exercise.name,
            'total_users': logs.values('user').distinct().count(),
            'total_sessions': logs.values('user', 'date').distinct().count(),
            'total_sets': logs.count(),
            'average_weight': logs.aggregate(avg_weight=Avg('weight'))['avg_weight'] or 0,
            'max_weight': logs.aggregate(max_weight=Max('weight'))['max_weight'] or 0,
            'average_feedback_score': logs.filter(
                feedback_score__isnull=False
            ).aggregate(avg_score=Avg('feedback_score'))['avg_score'] or 0,
        }
        
        return Response(analytics_data)


class WorkoutPlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar planes de entrenamiento.
    
    Endpoints:
    - GET /api/plans/ - Lista todos los planes públicos
    - POST /api/plans/ - Crear un nuevo plan
    - GET /api/plans/{id}/ - Detalle de un plan
    - PUT/PATCH /api/plans/{id}/ - Actualizar un plan
    - DELETE /api/plans/{id}/ - Eliminar un plan
    """
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Filtrar planes basado en el usuario y permisos.
        """
        user = self.request.user
        
        if self.action in ['list']:
            # Para listar, mostrar solo planes públicos y propios
            return WorkoutPlan.objects.filter(
                Q(is_public=True) | Q(creator=user)
            ).select_related('creator').prefetch_related('workout_days__workout_exercises__exercise')
        else:
            # Para otras acciones, filtrar por permisos de propiedad
            return WorkoutPlan.objects.filter(
                Q(is_public=True) | Q(creator=user)
            ).select_related('creator').prefetch_related('workout_days__workout_exercises__exercise')

    def get_serializer_class(self):
        """
        Retornar el serializer apropiado basado en la acción.
        """
        if self.action == 'create':
            return WorkoutPlanCreateSerializer
        return WorkoutPlanSerializer

    def perform_create(self, serializer):
        """
        Asignar el usuario actual como creador del plan.
        """
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        """
        Seguir un plan de entrenamiento.
        """
        plan = self.get_object()
        user = request.user
        
        # Verificar si ya está siguiendo este plan
        existing = UserWorkoutPlan.objects.filter(
            user=user, 
            workout_plan=plan, 
            is_active=True
        ).first()
        
        if existing:
            return Response(
                {'detail': 'Ya estás siguiendo este plan.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Desactivar otros planes activos
        UserWorkoutPlan.objects.filter(
            user=user, 
            is_active=True
        ).update(is_active=False, end_date=timezone.now().date())
        
        # Crear nueva asociación
        user_plan = UserWorkoutPlan.objects.create(
            user=user,
            workout_plan=plan,
            start_date=timezone.now().date(),
            is_active=True
        )
        
        serializer = UserWorkoutPlanSerializer(user_plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def unfollow(self, request, pk=None):
        """
        Dejar de seguir un plan de entrenamiento.
        """
        plan = self.get_object()
        user = request.user
        
        try:
            user_plan = UserWorkoutPlan.objects.get(
                user=user,
                workout_plan=plan,
                is_active=True
            )
            user_plan.is_active = False
            user_plan.end_date = timezone.now().date()
            user_plan.save()
            
            return Response({'detail': 'Plan abandonado exitosamente.'})
        except UserWorkoutPlan.DoesNotExist:
            return Response(
                {'detail': 'No estás siguiendo este plan.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserPerformanceLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar logs de rendimiento del usuario.
    
    Endpoints:
    - GET /api/log/ - Lista logs del usuario
    - POST /api/log/ - Crear un nuevo log
    - GET /api/log/{id}/ - Detalle de un log
    - PUT/PATCH /api/log/{id}/ - Actualizar un log
    - DELETE /api/log/{id}/ - Eliminar un log
    """
    
    serializer_class = UserPerformanceLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['date', 'workout_exercise__exercise']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date', '-created_at']

    def get_queryset(self):
        """
        Filtrar logs por usuario autenticado.
        """
        return UserPerformanceLog.objects.filter(
            user=self.request.user
        ).select_related(
            'workout_exercise__exercise',
            'workout_exercise__workout_day__plan'
        )

    def perform_create(self, serializer):
        """
        Asignar el usuario actual al log.
        """
        serializer.save(user=self.request.user)


class UserProgressView(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para obtener el progreso del usuario.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def exercise_progress(self, request):
        """
        Obtener el progreso del usuario en un ejercicio específico.
        
        Query params:
        - exercise_id: ID del ejercicio
        """
        exercise_id = request.query_params.get('exercise_id')
        
        if not exercise_id:
            return Response(
                {'detail': 'exercise_id es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            exercise = Exercise.objects.get(id=exercise_id)
        except Exercise.DoesNotExist:
            return Response(
                {'detail': 'Ejercicio no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener logs del usuario para este ejercicio
        logs = UserPerformanceLog.objects.filter(
            user=request.user,
            workout_exercise__exercise=exercise
        ).order_by('date')
        
        if not logs.exists():
            return Response(
                {'detail': 'No hay datos de progreso para este ejercicio.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calcular estadísticas
        total_sessions = logs.values('date').distinct().count()
        total_sets = logs.count()
        total_reps = sum(log.reps_completed for log in logs)
        max_weight = logs.aggregate(max_weight=Max('weight'))['max_weight']
        average_weight = logs.aggregate(avg_weight=Avg('weight'))['avg_weight']
        latest_session = logs.last().date
        average_feedback_score = logs.filter(
            feedback_score__isnull=False
        ).aggregate(avg_score=Avg('feedback_score'))['avg_score'] or 0
        
        # Datos de progreso por fecha
        progress_data = []
        for log in logs.values('date').annotate(
            max_weight=Max('weight'),
            avg_weight=Avg('weight'),
            total_sets=Count('id'),
            avg_feedback=Avg('feedback_score')
        ).order_by('date'):
            progress_data.append({
                'date': log['date'],
                'max_weight': float(log['max_weight']),
                'avg_weight': float(log['avg_weight']),
                'total_sets': log['total_sets'],
                'avg_feedback_score': log['avg_feedback'] or 0
            })
        
        progress_info = {
            'exercise_id': exercise.id,
            'exercise_name': exercise.name,
            'total_sessions': total_sessions,
            'total_sets': total_sets,
            'total_reps': total_reps,
            'max_weight': float(max_weight),
            'average_weight': float(average_weight),
            'latest_session': latest_session,
            'average_feedback_score': average_feedback_score,
            'progress_data': progress_data
        }
        
        serializer = UserProgressSerializer(progress_info)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Obtener datos del dashboard del usuario.
        """
        user = request.user
        
        # Estadísticas generales
        total_workouts = UserPerformanceLog.objects.filter(
            user=user
        ).values('date').distinct().count()
        
        total_exercises = UserPerformanceLog.objects.filter(
            user=user
        ).values('workout_exercise__exercise').distinct().count()
        
        total_sets = UserPerformanceLog.objects.filter(user=user).count()
        
        # Plan actual
        current_plan = UserWorkoutPlan.objects.filter(
            user=user,
            is_active=True
        ).select_related('workout_plan').first()
        
        # Último entrenamiento
        last_log = UserPerformanceLog.objects.filter(
            user=user
        ).order_by('-date').first()
        
        # Ejercicios más frecuentes
        frequent_exercises = UserPerformanceLog.objects.filter(
            user=user
        ).values(
            'workout_exercise__exercise__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        dashboard_data = {
            'total_workouts': total_workouts,
            'total_exercises': total_exercises,
            'total_sets': total_sets,
            'current_plan': WorkoutPlanSerializer(
                current_plan.workout_plan
            ).data if current_plan else None,
            'last_workout_date': last_log.date if last_log else None,
            'frequent_exercises': list(frequent_exercises)
        }
        
        return Response(dashboard_data)
