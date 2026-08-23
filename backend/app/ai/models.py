from django.conf import settings
from django.db import models
import uuid


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="chats")
    title = models.CharField(max_length=255,blank=True,default="Новый чат")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title

class ChatMessage(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
        ("system", "System"),
    ]

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    content = models.TextField()
    
    sources = models.JSONField(
        default=list,
        blank=True,
    )

    class Meta:
        ordering = ["created_at"]




class ReferenceEmbedding(models.Model):

    DOMAIN_CHOICES = [
        ("catalog", "Catalog"),
        ("service", "Service"),
        ("general", "General"),
    ]

    text = models.TextField(unique=True)

    domain = models.CharField(
        max_length=20,
        choices=DOMAIN_CHOICES,
    )

    embedding = models.JSONField()

    def __str__(self):
        return f"{self.domain}: {self.text[:50]}"