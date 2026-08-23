from rest_framework import serializers

from app.ai.models import Chat, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ("id", "role", "content", "created_at", "sources")


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ("id", "title", "created_at", "updated_at")

class ChatCreateSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, allow_blank=True, default="")


class AskSerializer(serializers.Serializer):
    message = serializers.CharField()
    chat_id = serializers.UUIDField(required=False,allow_null=True,default=None,)


class SourceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class AnswerSerializer(serializers.Serializer):
    chat_id = serializers.UUIDField(required=False,allow_null=True,default=None,)
    answer = serializers.CharField()
    sources = SourceSerializer(many=True)