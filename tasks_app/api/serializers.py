from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.generics import get_object_or_404

from django.contrib.auth import get_user_model

from boards_app.models import Board
from .models import Task

User = get_user_model()


class UserMiniSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "fullname")

    def get_fullname(self, obj):
        return f"{obj.fullname}"


class TaskCreateSerializer(serializers.ModelSerializer):
    board = serializers.IntegerField(write_only=True)
    board_id = serializers.IntegerField(source="board.id", read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source="reviewer",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    assignee = UserMiniSerializer(read_only=True)
    reviewer = UserMiniSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

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
        board_id = data.get("board")
        if not board_id:
            raise serializers.ValidationError({"board": "Board is required."})

        board = get_object_or_404(Board, pk=data.get("board"))
        user = self.context["request"].user
        if user not in board.members.all():
            raise PermissionDenied("You must be a member of the board.")  # <- 403

        for role in ["assignee", "reviewer"]:
            candidate = data.get(role)
            if candidate and candidate not in board.members.all():
                raise serializers.ValidationError(
                    {role: f"{role.capitalize()} must be a member of the board."}
                )

        data["board"] = board
        return data


# ----------------------------------
""" try:
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            raise NotFound("Board not found.") """

# TaskSerializer:  ersetzt durch    board =
# ----------------------------------


class TaskUpdateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source="reviewer",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
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
        task: Task = self.instance
        board = task.board
        user = self.context["request"].user

        if user not in board.members.all():
            raise PermissionDenied(
                "You must be a member of the board to update this task."
            )

        for role in ["assignee", "reviewer"]:
            candidate = data.get(role)
            if candidate and candidate not in board.members.all():
                raise serializers.ValidationError(
                    {role: f"{role.capitalize()} must be a member of the board."}
                )

        return data


class AssignedToMeAndReviewingSerializer(serializers.ModelSerializer):
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
        # Falls du ein Comment-Modell hast → replace with obj.comments.count()
        return getattr(obj, "comments_count", 0)
