import requests
import xml.etree.ElementTree as ET

from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, BasePermission, AllowAny, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken

from drf_spectacular.utils import extend_schema

from app.accounts.serializers import UserSerializer, RegisterSerializer, LoginSerializer
from app.accounts.models import User
from app.accounts.services import AccountService


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


class CASCallbackView(APIView):
    """
    Шаг 2–5 CAS-протокола:
      GET /accounts/cas/callback/?ticket=ST-xxxxx
    
    1. Получаем ticket из query string
    2. Валидируем через serviceValidate на сервере CAS МГТУ
    3. Парсим XML-ответ, извлекаем username
    4. Находим или создаём пользователя Django
    5. Генерируем JWT-токены и редиректим на frontend
    """
    permission_classes = [AllowAny]

    def get(self, request):
        ticket = request.GET.get('ticket')
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')

        # Если ticket отсутствует — редирект на страницу входа с ошибкой
        if not ticket:
            return redirect(f"{frontend_url}/auth?error=no_ticket")

        cas_server = settings.CAS_SERVER_URL.rstrip('/')
        service_url = settings.CAS_SERVICE_URL
        validate_url = f"{cas_server}/serviceValidate"

        try:
            # Шаг 3: валидируем ticket на сервере CAS
            response = requests.get(
                validate_url,
                params={'service': service_url, 'ticket': ticket},
                timeout=10,
                verify=True,  # Проверка SSL-сертификата
            )
            response.raise_for_status()
        except requests.RequestException as e:
            return redirect(f"{frontend_url}/auth?error=cas_unreachable")

        # Шаг 4: парсим XML-ответ
        try:
            ns = {'cas': 'http://www.yale.edu/tp/cas'}
            root = ET.fromstring(response.text)
            success_node = root.find('cas:authenticationSuccess', ns)

            if success_node is None:
                # CAS вернул authenticationFailure — невалидный ticket
                failure_node = root.find('cas:authenticationFailure', ns)
                error_code = failure_node.attrib.get('code', 'UNKNOWN') if failure_node is not None else 'UNKNOWN'
                return redirect(f"{frontend_url}/auth?error=cas_failed&code={error_code}")

            cas_username = success_node.find('cas:user', ns).text.strip()

        except ET.ParseError:
            return redirect(f"{frontend_url}/auth?error=cas_parse_error")

        # Шаг 5: находим или создаём пользователя
        user, created = User.objects.get_or_create(
            username=cas_username,
            defaults={'is_active': True}
        )

        # Генерируем JWT-токены
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Редирект на frontend с токенами в query string
        params = urlencode({'access': access_token, 'refresh': refresh_token})
        return redirect(f"{frontend_url}/cas-callback?{params}")
