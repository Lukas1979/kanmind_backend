from django.contrib import admin
from tasks_app.api.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "board", "status", "priority", "assignee", "reviewer", "due_date", "created_at")
    list_filter = ("board", "status", "priority", "due_date")
    search_fields = ("title", "description", "assignee__username", "reviewer__username")
    autocomplete_fields = ("assignee", "reviewer", "board")
    ordering = ("-created_at",)
