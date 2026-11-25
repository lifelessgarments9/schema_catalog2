import logging
import secrets
import time
from urllib.parse import urlencode, urlparse

import requests
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect
from django.utils.crypto import constant_time_compare
from django.utils import timezone
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
SSO_LOGIN_TICKET_TTL = 120


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

    def get(self, request):
        expected_state = request.session.pop("sso_oauth_state", None)
        received_state = request.query_params.get("state", "")
        if (
            not expected_state
            or not isinstance(received_state, str)
            or not constant_time_compare(expected_state, received_state)
        ):
            return sso_error_redirect("sso_state")

        sso_error = request.query_params.get("error")
        if sso_error:
            return sso_error_redirect(
                "sso_denied" if sso_error == "access_denied" else "sso_error"
            )

        code = request.query_params.get("code")
        if not isinstance(code, str) or not code:
            return sso_error_redirect("sso_code")

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
                    "BMSTU rejected the authorization code with HTTP %s",
                    token_response.status_code,
                )
                return sso_error_redirect("sso_exchange")

            token_data = token_response.json()
            access_token = token_data.get("access_token") if isinstance(token_data, dict) else None
            if not isinstance(access_token, str) or not access_token:
                logger.error("BMSTU token response did not contain an access token")
                return sso_error_redirect("sso_exchange")

            userinfo_response = requests.get(
                f"{settings.SSO_BASE_URL}/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            )
            userinfo_response.raise_for_status()
            userinfo = userinfo_response.json()
        except (requests.RequestException, ValueError):
            logger.exception("BMSTU SSO token or userinfo request failed")
            return sso_error_redirect("sso_unavailable")

        person = userinfo.get("person", userinfo) if isinstance(userinfo, dict) else None
        if not isinstance(person, dict):
            logger.error("BMSTU returned an invalid userinfo response")
            return sso_error_redirect("sso_userinfo")

        identity = person.get("guid") or person.get("id")
        if not identity:
            logger.error("BMSTU userinfo response did not contain a user identity")
            return sso_error_redirect("sso_userinfo")

        username = f"sso_{identity}"
        if len(username) > 150:
            logger.error("BMSTU user identity exceeds the supported username length")
            return sso_error_redirect("sso_userinfo")

        user = User.objects.filter(username=username).first()
        if user and user.has_usable_password():
            return sso_error_redirect("sso_account_conflict")
        if not user:
            user = User.objects.create(
                username=username,
                password=make_password(None),
            )
        if not user.is_active:
            return sso_error_redirect("sso_inactive")

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
        request.session.cycle_key()
        request.session["sso_access_token"] = access_token
        ticket = secrets.token_urlsafe(32)
        request.session["sso_login_ticket"] = ticket
        request.session["sso_login_ticket_created_at"] = timezone.now().timestamp()
        request.session["sso_login_tokens"] = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
        return redirect(
            f"{settings.FRONTEND_URL.rstrip('/')}/sso/callback/#ticket={ticket}"
        )


class SSOCompleteView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ticket = request.data.get("ticket")
        expected_ticket = request.session.get("sso_login_ticket")
        created_at = request.session.get("sso_login_ticket_created_at")

        if (
            not isinstance(ticket, str)
            or not isinstance(expected_ticket, str)
            or not constant_time_compare(expected_ticket, ticket)
        ):
            return Response({"detail": "Invalid SSO login ticket."}, status=status.HTTP_400_BAD_REQUEST)

        now = time.time()
        if (
            not isinstance(created_at, (int, float))
            or created_at > now
            or now - created_at > SSO_LOGIN_TICKET_TTL
        ):
            request.session.pop("sso_login_ticket", None)
            request.session.pop("sso_login_ticket_created_at", None)
            request.session.pop("sso_login_tokens", None)
            return Response({"detail": "SSO login ticket expired."}, status=status.HTTP_400_BAD_REQUEST)

        tokens = request.session.get("sso_login_tokens")
        if (
            not isinstance(tokens, dict)
            or not isinstance(tokens.get("access"), str)
            or not isinstance(tokens.get("refresh"), str)
        ):
            return Response({"detail": "SSO login result is unavailable."}, status=status.HTTP_400_BAD_REQUEST)

        request.session.pop("sso_login_ticket", None)
        request.session.pop("sso_login_ticket_created_at", None)
        request.session.pop("sso_login_tokens", None)
        return Response(tokens)


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
