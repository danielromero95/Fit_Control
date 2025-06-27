from rest_framework import generics
from rest_framework.exceptions import NotFound

from .models import Workout
from .serializers import WorkoutSerializer


class WorkoutListView(generics.ListAPIView):
    queryset = Workout.objects.prefetch_related("entries__exercise").all()
    serializer_class = WorkoutSerializer


class WorkoutDetailView(generics.RetrieveAPIView):
    """Retrieve a workout by its date (YYYY-MM-DD)."""

    queryset = Workout.objects.prefetch_related("entries__exercise").all()
    serializer_class = WorkoutSerializer
    lookup_field = "workout_date"

    def get_object(self):
        try:
            return super().get_object()
        except Exception as exc:  # generic 404 handling when date format invalid
            raise NotFound("Workout not found") from exc
