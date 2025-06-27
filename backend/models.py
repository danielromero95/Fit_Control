from django.db import models

class Exercise(models.Model):
    """
    Representa un único tipo de ejercicio que puede ser realizado,
    como "Press de Banca" o "Sentadillas".
    """
    name = models.CharField(
        max_length=255, 
        unique=True, 
        help_text="El nombre del ejercicio."
    )

    def __str__(self) -> str:
        """Devuelve el nombre del ejercicio como su representación en cadena."""
        return self.name

    class Meta:
        ordering = ['name']


class Workout(models.Model):
    """
    Representa una sesión de entrenamiento completa realizada en una fecha específica.
    Agrupa varias entradas de ejercicios (WorkoutEntry).
    """
    workout_date = models.DateField(
        db_index=True, 
        help_text="La fecha en que se realizó el entrenamiento."
    )
    exercises = models.ManyToManyField(
        Exercise,
        through='WorkoutEntry',
        related_name='workouts',
        help_text="Ejercicios realizados en esta sesión de entrenamiento."
    )

    def __str__(self) -> str:
        """Devuelve una representación legible del entrenamiento, incluyendo la fecha."""
        return f"Entrenamiento del {self.workout_date.strftime('%d-%m-%Y')}"

    class Meta:
        ordering = ['-workout_date']


class WorkoutEntry(models.Model):
    """
    Modelo intermedio que detalla un ejercicio específico dentro de un Workout.
    Almacena las series, repeticiones y peso para ese ejercicio en esa sesión.
    """
    workout = models.ForeignKey(
        Workout, 
        on_delete=models.CASCADE, 
        related_name="entries"
    )
    exercise = models.ForeignKey(
        Exercise, 
        on_delete=models.CASCADE, 
        related_name="workout_entries"
    )
    sets = models.PositiveIntegerField(help_text="Número de series realizadas.")
    reps = models.PositiveIntegerField(help_text="Número de repeticiones por serie.")
    weight_kg = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        help_text="Peso levantado en kilogramos."
    )

    def __str__(self) -> str:
        """Devuelve un resumen detallado de la entrada del ejercicio."""
        return f"{self.exercise.name}: {self.sets}x{self.reps} @ {self.weight_kg} kg"

    class Meta:
        # Evita que se pueda añadir el mismo ejercicio dos veces en el mismo workout
        unique_together = ('workout', 'exercise')
        ordering = ['id']