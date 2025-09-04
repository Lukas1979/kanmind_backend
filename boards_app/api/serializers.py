from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from ..models import Board
from tasks_app.api.models import Task

User = get_user_model()


class BoardSerializer(serializers.ModelSerializer):
    """
    This is a Django REST Framework (DRF) serializer for the board model.
    It defines how board data is transferred, validated, and created, including relationships to members and tasks.
    """
    
    members = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.ReadOnlyField(source="owner.id")

    class Meta:
        model = Board
        fields = ["id", "title", "members", "member_count", "ticket_count", "tasks_to_do_count", "tasks_high_prio_count", "owner_id"]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()

    def validate_members(self, value):
        users = User.objects.filter(id__in=value)
        if users.count() != len(value):
            missing_ids = set(value) - set(users.values_list("id", flat=True))
            raise serializers.ValidationError(
                f"The following user IDs (members) do not exist: {list(missing_ids)}"
            )
        return value

    def create(self, validated_data):
        members_ids = validated_data.pop("members", [])
        user = self.context["request"].user
        board = Board.objects.create(owner=user, **validated_data)
        members = User.objects.filter(id__in=members_ids)
        board.members.set(members)
        return board


class UserMiniSerializer(serializers.ModelSerializer):
    """
    This is a compact serializer for the User model that transmits only the most important information about a user.
    """

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class TaskListSerializer(serializers.ModelSerializer):
    """
    Das ist ein Django REST Framework (DRF) Serializer für das Task-Modell, 
    der Aufgaben zusammen mit zugehörigen Informationen über Benutzer und Kommentare darstellt.
    """
    
    assignee = UserMiniSerializer(read_only=True)
    reviewer = UserMiniSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()
    creator_id = serializers.IntegerField(source="creator.id", read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
            "creator_id"
        )

    def get_comments_count(self, obj):
        return obj.comments.count()
    

class BoardDetailSerializer(serializers.ModelSerializer):
    """
    This is a Django REST Framework (DRF) serializer for the board model 
    that provides detailed information about a board, including members and tasks.
    """
    
    members = UserMiniSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]

    def get_tasks(self, obj):
        tasks = obj.tasks.all()
        return TaskListSerializer(tasks, many=True).data


class BoardUpdateSerializer(serializers.ModelSerializer):
    """
    This is a Django REST Framework (DRF) serializer for the board model, 
    used to update a board, specifically its title and members.
    """
    
    title = serializers.CharField(required=False)
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False, write_only=True)
    owner_data = UserMiniSerializer(source="owner", read_only=True)
    members_data = UserMiniSerializer(source="members", many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "members", "owner_data", "members_data"]

    def update(self, instance, validated_data):
        if "title" in validated_data:
            instance.title = validated_data["title"]

        if "members" in validated_data:
            instance.members.set(validated_data["members"])

        instance.save()
        return instance


class EmailCheckSerializer(serializers.Serializer):
    """
    This is a Django REST Framework (DRF) serializer that checks whether an email address belongs 
    to an existing user and returns the user data.
    """
    
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        user = get_object_or_404(User, email=email)
        return {"id": user.id, "email": user.email, "fullname": user.fullname}
