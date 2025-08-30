from django.urls import path

from .views import TaskCreateView, TaskUpdateDeleteView, AssignedToMeView, ReviewingView, CommentListCreateView, CommentDeleteView


urlpatterns = [
    path("", TaskCreateView.as_view(), name="task-create"),
    path("<int:pk>/", TaskUpdateDeleteView.as_view(), name="task-update-delete"),
    path("assigned-to-me/", AssignedToMeView.as_view(), name="assigned-to-me"),
    path("reviewing/", ReviewingView.as_view(), name="reviewing"),
    path("<int:task_id>/comments/", CommentListCreateView.as_view(), name="comment-create"),
    path("<int:task_id>/comments/<int:comment_id>/", CommentDeleteView.as_view(), name="task-comment-delete")
]
