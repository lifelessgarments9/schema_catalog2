from django.urls import path

from app.accounts.views import (
    UserListView,
    RegisterView,
    ProfileView,
    LoginView,
    SSOLoginView,
    SSOCallbackView,
)

urlpatterns = [
    path("users/", UserListView.as_view(), name="user-list"),
    path("register/", RegisterView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("login/", LoginView.as_view()),
]
