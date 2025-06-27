from rest_framework import serializers

from .models import Exercise, WorkoutEntry, Workout


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ["id", "name"]


class WorkoutEntrySerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)

    class Meta:
        model = WorkoutEntry
        fields = ["id", "exercise", "sets", "reps", "weight_kg"]


class WorkoutSerializer(serializers.ModelSerializer):
    entries = WorkoutEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Workout
        fields = ["id", "workout_date", "entries"]
