import logging
import secrets
from urllib.parse import urlencode, urlparse

import requests
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect
from django.utils.crypto import constant_time_compare
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, BasePermission, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from app.accounts.models import User
from app.accounts.serializers import UserSerializer, RegisterSerializer, LoginSerializer
from app.accounts.services import AccountService

logger = logging.getLogger(__name__)


class IsNotAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_authenticated


class UserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        return Response(UserSerializer(users, many=True).data)


class RegisterView(APIView):
    permission_classes = [IsNotAuthenticated]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: UserSerializer},
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = AccountService.register(
            username=serializer.validated_data["username"],
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [IsNotAuthenticated]

    @extend_schema(
        request=LoginSerializer,
        responses={201: UserSerializer},
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response({
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        responses={200: UserSerializer},
    )
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    @extend_schema(
        request=UserSerializer,
        responses={200: UserSerializer},
    )
    def patch(self, request):
        user = AccountService.update_profile(request.user.id, request.data)
        return Response(UserSerializer(user).data)


def sso_error_redirect(error):
    frontend_url = settings.FRONTEND_URL.rstrip("/")
    return redirect(f"{frontend_url}/auth?{urlencode({'error': error})}")


class SSOLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        sso_url = urlparse(settings.SSO_BASE_URL)
        callback_url = urlparse(settings.SSO_REDIRECT_URI)
        frontend_url = urlparse(settings.FRONTEND_URL)
        if not all((
            settings.SSO_BASE_URL,
            settings.SSO_CLIENT_ID,
            settings.SSO_CLIENT_SECRET,
            settings.SSO_REDIRECT_URI,
            settings.FRONTEND_URL,
        )):
            return sso_error_redirect("sso_config")

        if (
            sso_url.scheme != "https"
            or not sso_url.hostname
            or callback_url.scheme != "https"
            or not callback_url.hostname
            or (not settings.DEBUG and frontend_url.scheme != "https")
        ):
            return sso_error_redirect("sso_https")

        state = secrets.token_urlsafe(32)
        request.session["sso_oauth_state"] = state
        params = urlencode({
            "response_type": "code",
            "client_id": settings.SSO_CLIENT_ID,
            "redirect_uri": settings.SSO_REDIRECT_URI,
            "state": state,
        })
        return redirect(f"{settings.SSO_BASE_URL}/authorize?{params}")


class SSOCallbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        expected_state = request.session.pop("sso_oauth_state", None)
        received_state = request.data.get("state", "")
        if (
            not expected_state
            or not isinstance(received_state, str)
            or not constant_time_compare(expected_state, received_state)
        ):
            return Response({"detail": "Invalid OAuth state."}, status=status.HTTP_400_BAD_REQUEST)

        code = request.data.get("code")
        if not isinstance(code, str) or not code:
            return Response({"detail": "Missing authorization code."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token_response = requests.post(
                f"{settings.SSO_BASE_URL}/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": settings.SSO_CLIENT_ID,
                    "client_secret": settings.SSO_CLIENT_SECRET,
                    "redirect_uri": settings.SSO_REDIRECT_URI,
                },
                timeout=10,
            )

            if not token_response.ok:
                logger.error(
                    "BMSTU TOKEN ERROR: status=%s, content_type=%s, body=%s",
                    token_response.status_code,
                    token_response.headers.get("Content-Type"),
                    token_response.text[:2000],
                )
                token_response.raise_for_status()

            token_data = token_response.json()
            access_token = token_data.get("access_token") if isinstance(token_data, dict) else None
            if not access_token:
                return Response(
                    {"detail": "SSO did not return an access token."},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            userinfo_response = requests.get(
                f"{settings.SSO_BASE_URL}/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            )
            userinfo_response.raise_for_status()
            userinfo = userinfo_response.json()
        except (requests.RequestException, ValueError):
            logger.exception("BMSTU SSO token or userinfo request failed")
            return Response({"detail": "SSO is temporarily unavailable."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        person = userinfo.get("person", userinfo) if isinstance(userinfo, dict) else None
        if not isinstance(person, dict):
            return Response({"detail": "Invalid SSO userinfo response."}, status=status.HTTP_502_BAD_GATEWAY)

        identity = person.get("guid") or person.get("id")
        if not identity:
            return Response({"detail": "SSO user identity is missing."}, status=status.HTTP_502_BAD_GATEWAY)

        username = f"sso_{identity}"
        if len(username) > 150:
            return Response({"detail": "SSO user identity is invalid."}, status=status.HTTP_502_BAD_GATEWAY)

        user = User.objects.filter(username=username).first()
        if user and user.has_usable_password():
            return Response({"detail": "SSO account conflicts with a local account."}, status=status.HTTP_409_CONFLICT)
        if not user:
            user = User.objects.create(
                username=username,
                password=make_password(None),
            )
        if not user.is_active:
            return Response({"detail": "This account is inactive."}, status=status.HTTP_403_FORBIDDEN)

        updated_fields = []
        for field, value in (
            ("email", person.get("email", "")),
            ("first_name", person.get("firstname", "")),
            ("last_name", person.get("lastname", "")),
        ):
            if value and getattr(user, field) != value:
                setattr(user, field, value)
                updated_fields.append(field)
        if updated_fields:
            user.save(update_fields=updated_fields)

        refresh = RefreshToken.for_user(user)
        request.session["sso_access_token"] = access_token
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })


class SSOLogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        access_token = request.session.pop("sso_access_token", None)
        request.session.flush()

        if access_token:
            try:
                response = requests.get(
                    f"{settings.SSO_BASE_URL}/logout",
                    params={"type": "server"},
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10,
                )
                response.raise_for_status()
            except requests.RequestException:
                logger.exception("BMSTU SSO logout request failed")
                return Response(
                    {"detail": "Could not end the SSO session."},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

        return Response(status=status.HTTP_204_NO_CONTENT)
