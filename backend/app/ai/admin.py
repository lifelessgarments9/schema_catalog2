
from django.contrib import admin
from .models import Chat, ChatMessage


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    fields = ['role', 'content']


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title_preview', 'message_count']
    list_filter = ['user']
    search_fields = ['user__username', 'title', 'messages__content']
    inlines = [ChatMessageInline]

    def title_preview(self, obj):
        return obj.title or f"Чат #{obj.pk}"
    title_preview.short_description = 'Заголовок'

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Сообщений'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat_user', 'chat_title', 'role', 'content_preview']
    list_filter = ['role', 'chat__user']
    search_fields = ['content', 'chat__user__username', 'chat__title']
    autocomplete_fields = ['chat']  

    def chat_user(self, obj):
        return obj.chat.user.username
    chat_user.short_description = 'Пользователь'
    chat_user.admin_order_field = 'chat__user'

    def chat_title(self, obj):
        return obj.chat.title or f"Чат #{obj.chat.pk}"
    chat_title.short_description = 'Чат'

    def content_preview(self, obj):
        return obj.content[:100] + ('...' if len(obj.content) > 100 else '')
    content_preview.short_description = 'Сообщение'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "chat":
            kwargs["queryset"] = Chat.objects.select_related("user").all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)