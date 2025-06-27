from django.urls import path

from .views import WorkoutListView, WorkoutDetailView

urlpatterns = [
    path("workouts/", WorkoutListView.as_view(), name="workout-list"),
    path("workouts/<slug:workout_date>/", WorkoutDetailView.as_view(), name="workout-detail"),
]
