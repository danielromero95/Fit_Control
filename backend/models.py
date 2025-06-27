from django.db import models

class Exercise(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name

class Workout(models.Model):
    workout_date = models.DateField(db_index=True)

    def __str__(self) -> str:
        return self.workout_date.isoformat()

class WorkoutEntry(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="entries")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()
    weight_kg = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.workout}: {self.exercise} - {self.sets}x{self.reps} @ {self.weight_kg}kg"
