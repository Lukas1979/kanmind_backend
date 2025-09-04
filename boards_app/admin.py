"""
This is the admin configuration for the board model, including a custom form.
It defines how boards are displayed, edited, and managed in the Django admin.
"""

from django import forms
from django.contrib import admin

from .models import Board


class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['members'].label_from_instance = lambda obj: f"{obj.email} (id {obj.id})"
        self.fields['owner'].label_from_instance = lambda obj: f"{obj.email} (id {obj.id})"


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    form = BoardForm
    list_display = ("id", "title", "owner", "owner_id", "member_count", "members_ids")
    filter_horizontal = ("members",)
    search_fields = ("title", "owner__username")

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = "member count"

    def members_ids(self, obj):
        return ", ".join(str(u.id) for u in obj.members.all())
    members_ids.short_description = "Member-IDs"
