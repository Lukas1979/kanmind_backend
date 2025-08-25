from django.db.models import Q

from rest_framework import generics, mixins, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404

from .models import Task
# from .permissions import IsBoardMember
from .serializers import TaskCreateSerializer, TaskUpdateSerializer, AssignedToMeAndReviewingSerializer


class TaskCreateView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    # permission_classes = [permissions.IsAuthenticated, IsBoardMember]


class TaskUpdateDeleteView(
    mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView
):
    queryset = Task.objects.all()
    serializer_class = TaskUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if instance.board.owner != user:
            raise PermissionDenied("Only the board owner can delete tasks.")
        instance.delete()


class AssignedToMeView(generics.ListAPIView):
    serializer_class = AssignedToMeAndReviewingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(assignee=user).select_related(
            "assignee", "reviewer", "board"
        )
    

class ReviewingView(generics.ListAPIView):
    serializer_class = AssignedToMeAndReviewingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(reviewer=user).select_related(
            "assignee", "reviewer", "board"
        )
