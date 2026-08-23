from django.utils import timezone
from datetime import timedelta
from app.catalog.embedding import EmbeddingService
from app.ai.analyzer import QueryAnalyzer
from app.ai.search import DeviceSearcher
from app.ai.context import ContextBuilder
from app.ai.generator import Generator
from app.ai.models import Chat, ChatMessage
from django.shortcuts import get_object_or_404
from app.ai.prompts import SERVICE_CONTEXT


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
        now = timezone.now()
        if user.ai_requests <= 0:
            if user.ai_restore_at and now < user.ai_restore_at:
                raise PermissionError("Daily request limit exceeded")
            user.ai_requests = 5
            user.ai_restore_at = None

        title = message[:30]
        if len(message) > 30: title += "..."
        chat = self.get_or_create_chat(user, chat_id, title=title)

        user_message = ChatMessage.objects.create(chat=chat, role="user", content=message)
        chat.save()

        analysis = QueryAnalyzer().analyze(message)

        print(f"analysis: {analysis}")

        if analysis["domain"] == "catalog":
            query_embedding = EmbeddingService.create(message)
            scored_devices = DeviceSearcher().search(query_embedding)
            context = ContextBuilder().build(scored_devices)
        elif analysis["domain"] == "service":
            scored_devices = []
            context = SERVICE_CONTEXT
        else:
            scored_devices = []
            context = ""
            user.ai_requests -= 1
            if user.ai_requests == 0:
                user.ai_restore_at = now + timedelta(hours=24)
            user.save(update_fields=["ai_requests","ai_restore_at",])

        answer = Generator().generate(message, context)

        sources = [
            {"id": device.pk, "name": device.name} for device, _score in scored_devices
        ]
        assistant_message = ChatMessage.objects.create(chat=chat, role="assistant", content=answer, sources=sources)
        chat.save()

        return {
            "chat_id": chat.pk,
            "messages": [
                {
                    "id": user_message.pk,
                    "role": "user",
                    "content": message,
                },
                {
                    "id": assistant_message.pk,
                    "role": "assistant",
                    "content": answer,
                    "sources": assistant_message.sources,
                },
            ],
        }

    def get_chats(self, user):
        return Chat.objects.filter(user=user).order_by("-updated_at")


    def get_chat_messages(self, user, chat_id: int):
        chat = get_object_or_404(Chat,pk=chat_id, user=user)
        return chat.messages.all()

    def delete_chat(self, user, chat_id: int) -> None:
        Chat.objects.filter(pk=chat_id, user=user).delete()