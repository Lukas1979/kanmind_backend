from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404

from boards_app.models import Board
from boards_app.api.serializers import UserMiniSerializer
from .models import Task, Comment

User = get_user_model()


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    This is a Django REST Framework (DRF) serializer for creating tasks within a board.
    It handles both input data validation and API response serialization.
    """
    
    board = serializers.IntegerField(write_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee", queryset=User.objects.all(), required=False,
        allow_null=True, write_only=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source="reviewer", queryset=User.objects.all(), required=False,
        allow_null=True, write_only=True,
    )
    assignee = UserMiniSerializer(read_only=True)
    reviewer = UserMiniSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()
    creator_id = serializers.IntegerField(source="creator.id", read_only=True)
    board_id = serializers.IntegerField(source="board.id", read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "board",
            "board_id",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
            "creator_id"
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        board_value = ret.pop("board_id")
        ret = {
            "id": ret.get("id"),
            "board": board_value,
            **{k: v for k, v in ret.items() if k != "id"},
        }
        return ret

    def get_comments_count(self, obj):
        return 0

    def validate(self, data):
        board = get_object_or_404(Board, pk=data.get("board"))
        user = self.context["request"].user
        if user not in board.members.all():
            raise PermissionDenied("You must be a member of the board.")  # <- 403

        for role in ["assignee", "reviewer"]:
            candidate = data.get(role)
            if candidate and candidate not in board.members.all():
                raise serializers.ValidationError({role: f"{role.capitalize()} must be a member of the board."})
        
        return {**data, "board": board, "creator": user}


class TaskUpdateSerializer(serializers.ModelSerializer):
    """
    This is a Django REST Framework (DRF) serializer for updating tasks within a board.
    It ensures that only authorized users can make changes and validates user assignments.
    """
    
    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee", queryset=User.objects.all(), required=False, allow_null=True, write_only=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source="reviewer", queryset=User.objects.all(), required=False, allow_null=True, write_only=True,
    )
    assignee = UserMiniSerializer(read_only=True)
    reviewer = UserMiniSerializer(read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "assignee",
            "reviewer",
            "due_date",
        )
        read_only_fields = ("id",)

    def validate(self, data):
        board = self.instance.board
        user = self.context["request"].user

        if user not in board.members.all():
            raise PermissionDenied("You must be a member of the board to update this task.")

        for role in ["assignee", "reviewer"]:
            candidate = data.get(role)
            if candidate and candidate not in board.members.all():
                raise serializers.ValidationError({role: f"{role.capitalize()} must be a member of the board."})
            
        return data


class AssignedToMeAndReviewingSerializer(serializers.ModelSerializer):
    """
    This is a Django REST Framework (DRF) serializer that presents tasks specifically to the user 
    that are assigned to them or that they are supposed to review.
    """
    
    assignee = UserMiniSerializer(read_only=True)
    reviewer = UserMiniSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()


class CommentListCreateSerializer(serializers.ModelSerializer):
    """
    This is a Django REST Framework (DRF) serializer that handles comments for display and creation operations in the API.
    """
    
    author = serializers.CharField(source="author.fullname", read_only=True)
    author_id = serializers.IntegerField(source="author.id", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "author_id", "content"]
        read_only_fields = ["id", "created_at"]
