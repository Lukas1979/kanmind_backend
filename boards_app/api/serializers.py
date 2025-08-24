from rest_framework import serializers
from rest_framework.exceptions import NotFound
from ..models import Board
from django.contrib.auth import get_user_model

User = get_user_model()


class BoardSerializer(serializers.ModelSerializer):
    members = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.ReadOnlyField(source="owner.id")

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "members",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return 0  # später dynamisch berechnen

    def get_tasks_to_do_count(self, obj):
        return 0  # später dynamisch berechnen

    def get_tasks_high_prio_count(self, obj):
        return 0  # später dynamisch berechnen

    def validate_members(self, value):
        users = User.objects.filter(id__in=value)
        if users.count() != len(value):
            missing_ids = set(value) - set(users.values_list("id", flat=True))
            raise serializers.ValidationError(
                f"The following user IDs do not exist: {list(missing_ids)}"
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
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

    def get_fullname(self, obj):
        return f"{obj.fullname}"


class BoardDetailSerializer(serializers.ModelSerializer):
    members = UserMiniSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "owner_id",
            "members",
            "tasks",
        ]

    def get_tasks(self, obj):
        # Aktuell noch leer zurückgeben
        return []


class BoardUpdateSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    title = serializers.CharField(required=False)

    class Meta:
        model = Board
        fields = ["title", "members"]

    def validate_members(self, value):
        users = User.objects.filter(id__in=value)
        if users.count() != len(value):
            missing_ids = set(value) - set(users.values_list("id", flat=True))
            raise serializers.ValidationError(
                f"The following user IDs do not exist: {list(missing_ids)}"
            )
        return value

    def update(self, instance, validated_data):
        if "title" in validated_data:
            instance.title = validated_data["title"]
            instance.save()

        if "members" in validated_data:
            members = User.objects.filter(id__in=validated_data["members"])
            instance.members.set(members)

        return instance


class EmailCheckSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(required=True)
    fullname = serializers.CharField(read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise NotFound(detail="Email not found.")

        attrs.clear()
        attrs["id"] = user.id
        attrs["email"] = user.email
        attrs["fullname"] = f"{user.fullname}"
        return attrs
