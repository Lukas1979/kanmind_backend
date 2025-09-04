from rest_framework import permissions


class IsBoardMemberOrOwner(permissions.BasePermission):
    """
    This is a custom permission class for Django REST Framework (DRF) that checks whether a user has access to a board object.
    """
    
    message = "Forbidden. The user must be either a member of the board or the owner of the board."

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return obj.owner_id == user.id or obj.members.filter(id=user.id).exists()


class IsBoardOwner(permissions.BasePermission):
    """
    This is a custom permission class for Django REST Framework (DRF) that checks whether a user is the owner of a board.
    """
    
    message = "Forbidden. The user must be the owner of the board to delete it."

    def has_object_permission(self, request, view, obj):
        return obj.owner_id == request.user.id
