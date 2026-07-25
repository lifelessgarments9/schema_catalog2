from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from app.ai.models import Chat

from app.ai.services import ChatService
from app.ai.serializers import (
    AskSerializer,
    ChatCreateSerializer,
    ChatSerializer,
    ChatMessageSerializer,
)


class AskView(APIView):
    """
    POST /ai/chat/
    Отправить вопрос. Создаёт новый чат если chat_id не передан.
    Возвращает ответ и список источников (устройств).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = ChatService().chat(
            user=request.user,
            message=serializer.validated_data["message"],
            chat_id=serializer.validated_data.get("chat_id"),
        )
        return Response(result, status=status.HTTP_200_OK)


class ChatListCreateView(APIView):
    """
    GET  /ai/chats/  — список чатов пользователя
    POST /ai/chats/  — создать новый чат
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        chats = ChatService().get_chats(request.user)
        return Response(ChatSerializer(chats, many=True).data)

    def post(self, request):
        serializer = ChatCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat = Chat.objects.create(
            user=request.user,
            title=serializer.validated_data.get("title", ""),
        )
        return Response(ChatSerializer(chat).data, status=status.HTTP_201_CREATED)


class ChatDetailView(APIView):
    """
    GET    /ai/chats/<id>/  — история сообщений чата
    DELETE /ai/chats/<id>/  — удалить чат
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        messages = ChatService().get_chat_messages(request.user, pk)
        return Response(ChatMessageSerializer(messages, many=True).data)

    def delete(self, request, pk):
        ChatService().delete_chat(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)