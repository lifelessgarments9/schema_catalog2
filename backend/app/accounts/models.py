from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    bio = models.TextField(blank=True, default="")
    ai_requests = models.PositiveIntegerField(default=5)
    ai_restore_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username