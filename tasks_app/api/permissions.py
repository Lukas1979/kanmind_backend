from rest_framework import generics, permissions

from .models import Board

""" 
class IsBoardMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
     """