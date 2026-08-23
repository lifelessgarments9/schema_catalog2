from django.urls import path

from app.ai.views import AskView, ChatListCreateView, ChatDetailView

urlpatterns = [
    path("chat/", AskView.as_view()),
    path("chats/", ChatListCreateView.as_view()),
    path("chats/<uuid:pk>/", ChatDetailView.as_view()),
]