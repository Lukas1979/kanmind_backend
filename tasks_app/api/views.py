from django.db.models import Q
from rest_framework import generics, mixins
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404

from .models import Task, Comment
from .serializers import TaskCreateSerializer, TaskUpdateSerializer, AssignedToMeAndReviewingSerializer, CommentListCreateSerializer


class TaskCreateView(generics.CreateAPIView):
    """
    POST /api/tasks/
    Creates a new task within a board.
    """

    queryset = Task.objects.all()
    serializer_class = TaskCreateSerializer


class TaskUpdateDeleteView(mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    """
    PATCH /api/tasks/{task_id}/
    Updates an existing task.

    DELETE /api/tasks/{task_id}/
    Deletes an existing task
    """
    
    queryset = Task.objects.all()
    serializer_class = TaskUpdateSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        user = self.request.user
        if instance.board.owner != user and instance.creator != user:
            raise PermissionDenied("Only the board owner or the task creator can delete tasks.")
        instance.delete()


class AssignedToMeView(generics.ListAPIView):
    """
    GET /api/tasks/assigned-to-me/
    Retrieves all tasks assigned to the currently authenticated user as `assignee`.
    """
    
    serializer_class = AssignedToMeAndReviewingSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(assignee=user).select_related("assignee", "reviewer", "board")


class ReviewingView(generics.ListAPIView):
    """
    GET /api/tasks/reviewing/
    Retrieves all tasks assigned to the currently authenticated user as `reviewer`.
    """

    serializer_class = AssignedToMeAndReviewingSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(reviewer=user).select_related("assignee", "reviewer", "board")


class CommentListCreateView(generics.ListCreateAPIView):
    """
    GET /api/tasks/{task_id}/comments/
    Retrieves all comments associated with a specific task.

    POST /api/tasks/{task_id}/comments/
    Creates a new comment for a specific task.
    """
    
    serializer_class = CommentListCreateSerializer

    def get_task(self):
        task_id = self.kwargs["task_id"]
        return get_object_or_404(Task, pk=task_id)

    def get_queryset(self):
        task = self.get_task()
        user = self.request.user

        if not task.board.members.filter(id=user.id).exists():
            raise PermissionDenied("You must be a member of the board to view comments.")

        return task.comments.all().order_by("created_at")
    
    def perform_create(self, serializer):
        task = self.get_task()
        user = self.request.user

        if not task.board.members.filter(id=user.id).exists():
            raise PermissionDenied("You must be a member of the board to post a comment.")

        serializer.save(task=task, author=user)


class CommentDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/tasks/{task_id}/comments/{comment_id}/
    Deletes a comment from a specific task.
    """
    
    lookup_url_kwarg = "comment_id"

    def get_queryset(self):
        task_id = self.kwargs["task_id"]
        task = get_object_or_404(Task, pk=task_id)
        return Comment.objects.filter(task=task)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("Only the author may delete this comment.")
        instance.delete()
