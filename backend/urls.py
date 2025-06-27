from django.urls import path

from .views import WorkoutListView

urlpatterns = [
    path("workouts/", WorkoutListView.as_view(), name="workout-list"),
]
