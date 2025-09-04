"""
This is the admin configuration for the Task and Comment models in Django. 
It defines how tasks and comments are displayed, filtered, and searched in the admin interface.
"""

from django.contrib import admin

from tasks_app.api.models import Task, Comment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "board_id", "board_owner", "board_members", "status", "priority", "assignee_id", "reviewer_id", "due_date", "created_at", "creator_id")
    list_filter = ("board", "status", "priority", "due_date")
    search_fields = ("title", "description", "assignee__username", "reviewer__username")
    autocomplete_fields = ("assignee", "reviewer", "board")
    ordering = ("-created_at",)

    def board_owner(self, obj):
        return obj.board.owner.id
    board_owner.short_description = "board owner id"

    def board_members(self, obj):
        return ", ".join([str(user.id) for user in obj.board.members.all()])
    board_members.short_description = "board members"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "task", "author", "author_id", "short_content", "created_at")
    list_filter = ("created_at", "task__board")
    search_fields = ("content", "author__username", "author__first_name", "author__last_name")
    ordering = ("-created_at",)

    def short_content(self, obj):
        return (obj.content[:50] + "...") if len(obj.content) > 50 else obj.content
    short_content.short_description = "Content"
