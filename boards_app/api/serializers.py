from rest_framework import serializers
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


# -----------------------------------------------------


"""  ohne validierung für members

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

    def create(self, validated_data):
        members_ids = validated_data.pop("members", [])
        user = self.context["request"].user
        board = Board.objects.create(owner=user, **validated_data)
        members = User.objects.filter(id__in=members_ids)
        board.members.set(members)
        return board
 """
