from django.urls import path
from .views import TaskCreateView, TaskUpdateDeleteView, AssignedToMeView, ReviewingView


urlpatterns = [
    path('', TaskCreateView.as_view(), name="task-create"),
    path('<int:pk>/', TaskUpdateDeleteView.as_view(), name="task-update-delete"),
    path("assigned-to-me/", AssignedToMeView.as_view(), name="assigned-to-me"),
    path("reviewing/", ReviewingView.as_view(), name="reviewing"),
]
