from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserProfileSerializer,
)

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED,)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh токен обязателен"},
                     status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Выход выполнен"},
                            status.HTTP_200_OK),
        except TokenError:

            return Response(
                {"error": "Токен недействителен или уже использован"},
                status.HTTP_400_BAD_REQUEST
            )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Пароль успешно изменён"})