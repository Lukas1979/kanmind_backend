from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Board
from .permissions import IsBoardMemberOrOwner, IsBoardOwner
from .serializers import (BoardSerializer, BoardDetailSerializer, BoardUpdateSerializer, EmailCheckSerializer)

User = get_user_model()


class BoardListCreateView(generics.ListCreateAPIView):
    """
    GET /api/boards/
    Retrieves a list of boards that the logged in user has either created or is a member of.

    POST /api/boards/
    Create a new board and add members.
    """

    serializer_class = BoardSerializer

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()


class BoardRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/boards/{board_id}/
    Retrieves the information of a specific board, along with its associated tasks.
    
    PATCH /api/boards/{board_id}/
    Updates the title or members of an existing board.

    DELETE /api/boards/{board_id}/
    Deletes a board.
    """

    http_method_names = ["get", "patch", "delete"]

    def get_serializer_class(self):
        if self.request.method in ["PATCH"]:
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def get_permissions(self):
        if self.request.method == "DELETE":
            self.permission_classes = [permissions.IsAuthenticated, IsBoardOwner]
        else:
            self.permission_classes = [permissions.IsAuthenticated, IsBoardMemberOrOwner]
        return super().get_permissions()

    def get_queryset(self):
        return Board.objects.all()

    
class EmailCheckView(APIView):
    """
    GET /api/email-check/?email=test@example.com
    Checks whether a specific email address is already assigned to a registered user.
    """
    
    def get(self, request, *args, **kwargs):
        serializer = EmailCheckSerializer(data=request.query_params)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.validated_data)
