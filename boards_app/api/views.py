from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Board
from .permissions import IsBoardMemberOrOwner
from .serializers import (
    BoardSerializer,
    BoardDetailSerializer,
    BoardUpdateSerializer,
    EmailCheckSerializer,
)

User = get_user_model()


class BoardListCreateView(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BoardRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BoardDetailSerializer
    queryset = Board.objects.all()

    def get_permissions(self):
        if self.request.method == "DELETE":
            from .permissions import IsBoardOwner

            self.permission_classes = [permissions.IsAuthenticated, IsBoardOwner]
        elif self.request.method in ["PATCH", "PUT"]:
            from .permissions import IsBoardMemberOrOwner

            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBoardMemberOrOwner,
            ]
        else:
            from .permissions import IsBoardMemberOrOwner

            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBoardMemberOrOwner,
            ]
        return super().get_permissions()

    def get_object(self):
        pk = self.kwargs.get("pk")
        try:
            obj = self.queryset.get(pk=pk)
        except Board.DoesNotExist:
            raise NotFound("Board not found. The specified board ID does not exist.")
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        return Response(
            {
                "id": instance.id,
                "title": instance.title,
                "owner_data": {
                    "id": instance.owner.id,
                    "email": instance.owner.email,
                    "fullname": f"{instance.owner.fullname}",
                },
                "members_data": [
                    {"id": m.id, "email": m.email, "fullname": m.fullname}
                    for m in instance.members.all()
                ],
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailCheckView(APIView):
    def get(self, request, *args, **kwargs):
        serializer = EmailCheckSerializer(data=request.query_params)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.validated_data)
