from rest_framework import generics

from .models import Workout
from .serializers import WorkoutSerializer


class WorkoutListView(generics.ListAPIView):
    queryset = Workout.objects.prefetch_related("entries__exercise").all()
    serializer_class = WorkoutSerializer
