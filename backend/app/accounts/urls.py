from django.urls import path

from app.accounts.views import UserListView, RegisterView, ProfileView, LoginView, CASCallbackView

urlpatterns = [
    path("users/", UserListView.as_view(), name="user-list"),
    path("register/", RegisterView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("login/", LoginView.as_view()),
    # CAS callback — шаг 2 протокола: CAS-сервер редиректит сюда с ticket'ом
    path("cas/callback/", CASCallbackView.as_view(), name="cas-callback"),
]
