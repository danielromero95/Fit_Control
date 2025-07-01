"""
Serializers para la aplicación workouts de Fit_Control.

Estos serializers convierten los modelos Django en formatos JSON 
para la API REST.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Exercise, 
    WorkoutPlan, 
    WorkoutDay, 
    WorkoutExercise, 
    UserPerformanceLog,
    UserWorkoutPlan
)


class ExerciseSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Exercise.
    """
    
    muscle_group_display = serializers.CharField(
        source='get_muscle_group_display', 
        read_only=True
    )
    difficulty_display = serializers.CharField(
        source='get_difficulty_display', 
        read_only=True
    )
    
    class Meta:
        model = Exercise
        fields = [
            'id', 'name', 'description', 'muscle_group', 'muscle_group_display',
            'video_url', 'difficulty', 'difficulty_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class WorkoutExerciseSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo WorkoutExercise.
    """
    
    exercise = ExerciseSerializer(read_only=True)
    exercise_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = WorkoutExercise
        fields = [
            'id', 'exercise', 'exercise_id', 'sets', 'reps', 
            'rest_period', 'order', 'notes'
        ]


class WorkoutDaySerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo WorkoutDay.
    """
    
    workout_exercises = WorkoutExerciseSerializer(many=True, read_only=True)
    day_of_week_display = serializers.CharField(
        source='get_day_of_week_display', 
        read_only=True
    )
    
    class Meta:
        model = WorkoutDay
        fields = [
            'id', 'day_of_week', 'day_of_week_display', 'name', 
            'workout_exercises'
        ]


class WorkoutPlanSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo WorkoutPlan.
    """
    
    creator_username = serializers.CharField(
        source='creator.username', 
        read_only=True
    )
    workout_days = WorkoutDaySerializer(many=True, read_only=True)
    followers_count = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkoutPlan
        fields = [
            'id', 'name', 'description', 'creator', 'creator_username',
            'is_public', 'workout_days', 'followers_count', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['creator', 'created_at', 'updated_at']
    
    def get_followers_count(self, obj):
        """Retorna el número de usuarios siguiendo este plan."""
        return obj.followers.filter(is_active=True).count()


class WorkoutPlanCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear un nuevo plan de entrenamiento.
    """
    
    workout_days = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = WorkoutPlan
        fields = ['name', 'description', 'is_public', 'workout_days']
    
    def create(self, validated_data):
        """
        Crear un plan de entrenamiento con sus días y ejercicios.
        """
        workout_days_data = validated_data.pop('workout_days', [])
        validated_data['creator'] = self.context['request'].user
        
        plan = WorkoutPlan.objects.create(**validated_data)
        
        for day_data in workout_days_data:
            exercises_data = day_data.pop('exercises', [])
            day = WorkoutDay.objects.create(plan=plan, **day_data)
            
            for i, exercise_data in enumerate(exercises_data):
                exercise_data['workout_day'] = day
                exercise_data['order'] = i + 1
                WorkoutExercise.objects.create(**exercise_data)
        
        return plan


class UserPerformanceLogSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo UserPerformanceLog.
    """
    
    exercise_name = serializers.CharField(
        source='workout_exercise.exercise.name', 
        read_only=True
    )
    muscle_group = serializers.CharField(
        source='workout_exercise.exercise.muscle_group',
        read_only=True
    )
    username = serializers.CharField(
        source='user.username', 
        read_only=True
    )
    
    class Meta:
        model = UserPerformanceLog
        fields = [
            'id', 'user', 'username', 'workout_exercise', 'exercise_name',
            'muscle_group', 'date', 'weight', 'reps_completed', 'set_number',
            'feedback_score', 'feedback_text', 'video_file', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']
    
    def create(self, validated_data):
        """
        Crear un log de rendimiento asociado al usuario autenticado.
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserWorkoutPlanSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo UserWorkoutPlan.
    """
    
    workout_plan = WorkoutPlanSerializer(read_only=True)
    workout_plan_id = serializers.IntegerField(write_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserWorkoutPlan
        fields = [
            'id', 'user', 'username', 'workout_plan', 'workout_plan_id',
            'start_date', 'end_date', 'is_active'
        ]
        read_only_fields = ['user']
    
    def create(self, validated_data):
        """
        Asociar un plan de entrenamiento con el usuario autenticado.
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserProgressSerializer(serializers.Serializer):
    """
    Serializer para mostrar el progreso del usuario en un ejercicio específico.
    """
    
    exercise_id = serializers.IntegerField()
    exercise_name = serializers.CharField()
    total_sessions = serializers.IntegerField()
    total_sets = serializers.IntegerField()
    total_reps = serializers.IntegerField()
    max_weight = serializers.DecimalField(max_digits=6, decimal_places=2)
    average_weight = serializers.DecimalField(max_digits=6, decimal_places=2)
    latest_session = serializers.DateField()
    average_feedback_score = serializers.FloatField()
    progress_data = serializers.ListField(
        child=serializers.DictField(),
        help_text="Datos de progreso por fecha"
    )


class ExerciseFilterSerializer(serializers.Serializer):
    """
    Serializer para filtros de ejercicios.
    """
    
    muscle_group = serializers.ChoiceField(
        choices=Exercise.MUSCLE_GROUP_CHOICES,
        required=False
    )
    difficulty = serializers.ChoiceField(
        choices=Exercise.DIFFICULTY_CHOICES,
        required=False
    )
    search = serializers.CharField(required=False)


class WorkoutSessionSerializer(serializers.Serializer):
    """
    Serializer para una sesión de entrenamiento en curso.
    """
    
    plan_id = serializers.IntegerField()
    day_of_week = serializers.IntegerField()
    started_at = serializers.DateTimeField()
    exercises_completed = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    current_exercise = serializers.IntegerField(required=False)
    session_notes = serializers.CharField(required=False)