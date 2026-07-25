from app.catalog.embedding import EmbeddingService
from app.ai.search import DeviceSearcher
from app.ai.context import ContextBuilder
from app.ai.generator import Generator
from app.ai.models import Chat, ChatMessage
from app.ai.serializers import ChatMessageSerializer
from django.shortcuts import get_object_or_404
from django.db import transaction

class ChatService:

    def get_or_create_chat(self, user, chat_id: int | None, title: str = "") -> Chat:
        if chat_id:
            return get_object_or_404(
                Chat,
                pk=chat_id,
                user=user
            )
        return Chat.objects.create(user=user, title=title)

    def chat(self, user, message: str, chat_id: int | None = None) -> dict:
        """
        RAG-пайплайн:
          1. Получить / создать чат
          2. Создать эмбеддинг вопроса
          3. Найти top-5 устройств
          4. Сформировать контекст
          5. Сгенерировать ответ Qwen
          6. Сохранить сообщения в БД
          7. Вернуть { answer, sources }
        """
        title = message[:30]
        if len(message) > 30: title += "..."
        chat = self.get_or_create_chat(user, chat_id, title=title)

        # Сохраняем вопрос пользователя
        user_message = ChatMessage.objects.create(chat=chat, role="user", content=message)

        # RAG pipeline
        query_embedding = EmbeddingService.create(message)
        scored_devices = DeviceSearcher().search(query_embedding)
        context = ContextBuilder().build(scored_devices)
        print("before ollama")
        print(len(context))
        answer = Generator().generate(message, context)
        print("after ollama")

        # Сохраняем ответ ассистента
        assistant_message = ChatMessage.objects.create(chat=chat, role="assistant", content=answer)

        sources = [
            {"id": device.pk, "name": device.name}
            for device, _score in scored_devices
        ]

        return {
            "chat_id": chat.pk,
            "messages": ChatMessageSerializer(
                [user_message, assistant_message],
                many=True
            ).data,
            "sources": sources,
        }

    def get_chats(self, user):
        return Chat.objects.filter(user=user).order_by("-updated_at")

    def get_chat_messages(self, user, chat_id: int):
        chat = Chat.objects.get(pk=chat_id, user=user)
        return chat.messages.all()

    def delete_chat(self, user, chat_id: int) -> None:
        Chat.objects.filter(pk=chat_id, user=user).delete()