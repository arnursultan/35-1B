from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .services.google import GoogleOAuthService


from .models import CustomUser

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["role"] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user_id"] = self.user.id
        data["email"] = self.user.email
        data["role"] = self.user.role
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)
    tokens    = serializers.SerializerMethodField()

    class Meta:
        model  = CustomUser
        fields = ["id", "email", "first_name", "last_name", "role", "password", "password2", "tokens"]
        read_only_fields = ["id", "tokens"]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

    def get_tokens(self, obj):
        refresh = RefreshToken.for_user(obj)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model  = CustomUser
        fields = ["id", "email", "first_name", "last_name", "full_name", "role", "created_at"]
        read_only_fields = ["id", "email", "role", "created_at"]

    def get_full_name(self, obj):
        return obj.full_name

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password2 = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Неверный текущий пароль")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password": "Пароли не совпадают"})
        validate_password(attrs["new_password"], self.context["request"].user)
        return attrs

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user

class GoogleCallbackSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate(self, attrs):
        code = attrs.get["code"]

        try:
            google_data = GoogleOAuthService.get_google_user_data(code)
        except Exception as e:
            raise serializers.ValidationError(f"Ошибка Google OAuth: {str(e)}")

        email       = google_data.get("email")
        google_id   = google_data.get("id")
        first_name  = google_data.get("given_name", "")
        last_name   = google_data.get("family_name", "")
        avatar      = google_data.get("picture", "")

        if not email:
            raise serializers.ValidationError("Google не вернул email")

        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                "first_name":   first_name,
                "last_name":    last_name,
                "google_id":    google_id,
                "avatar":       avatar,
                "role":         CustomUser.ROLE_CLIENT
            }
        )

        if not created:
            updated = False
            if not user.google_id:
                user.google_id = google_id
                updated = True
            if not user.avatar:
                user.avatar = avatar
                updated = True
            if updated:
                user.save()

        refresh = RefreshToken.for_user(user)
        refresh["email"]    = user.email
        refresh["role"]     = user.role

        attrs["tokens"] = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
        attrs["user"]       = user
        attrs["created"]    = created
        return attrs