from django.db import models

class Exercise(models.Model):
    """Represents a single exercise that can be part of a workout."""

    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Workout(models.Model):
    """Group of exercises performed on a specific date."""

    workout_date = models.DateField(db_index=True)
    exercises = models.ManyToManyField(Exercise, through="WorkoutEntry", related_name="workouts")

    def __str__(self) -> str:
        return f"Workout on {self.workout_date}" if self.workout_date else "Workout"


class WorkoutEntry(models.Model):
    """Intermediate model representing a set of an exercise in a workout."""

    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="entries")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="workout_entries")
    sets = models.IntegerField()
    reps = models.IntegerField()
    weight_kg = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.exercise.name}: {self.sets}x{self.reps} @ {self.weight_kg}kg"
