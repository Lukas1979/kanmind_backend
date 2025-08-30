from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Board(models.Model):
    title = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='boards')
    owner = models.ForeignKey(User, related_name='owned_boards', on_delete=models.CASCADE)
