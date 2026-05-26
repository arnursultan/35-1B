import logging

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from notifications.tasks import send_welcome_email

from .serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    GoogleCallbackSerializer,
    RegisterSerializer,
    UserProfileSerializer,
)
from .services.google import GoogleOAuthService

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        send_welcome_email.delay(user.id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")

            if not refresh_token:
                return Response(
                    {"error": "Refresh токен обязателен"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Выход выполнен"},
                status=status.HTTP_200_OK
            )

        except TokenError:
            return Response(
                {"error": "Токен недействителен или уже использован"},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Пароль успешно изменён"})


class GoogleAuthUrlView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        url = GoogleOAuthService.get_auth_url()
        return Response({"url": url})


class GoogleCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.query_params.get("code")

        if not code:
            return Response(
                {"error": "Code не передан"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = GoogleCallbackSerializer(data={"code": code})
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user = data["user"]
        created = data["created"]

        if created:
            send_welcome_email.delay(user.id)

        return Response({
            "message": "Новый аккаунт создан" if created else "Добро пожаловать",
            "email": user.email,
            "role": user.role,
            "tokens": data["tokens"],
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)