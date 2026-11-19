from django.urls import path

from app.accounts.views import (
    UserListView,
    RegisterView,
    ProfileView,
    LoginView,
    SSOLoginView,
    SSOCallbackView,
    SSOLogoutView,
)

urlpatterns = [
    path("users/", UserListView.as_view(), name="user-list"),
    path("register/", RegisterView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("login/", LoginView.as_view()),
    path("sso/login/", SSOLoginView.as_view(), name="sso-login"),
    path("sso/callback/", SSOCallbackView.as_view(), name="sso-callback"),
    path("sso/logout/", SSOLogoutView.as_view(), name="sso-logout"),
]
