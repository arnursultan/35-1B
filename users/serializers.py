from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model  = CustomUser
        fields = ["email", "first_name", "last_name", "role", "password", "password2"]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["email"],
            password=attrs["password"],
        )
        if not user:
            raise serializers.ValidationError("Неверный email или пароль")
        if not user.is_active:
            raise serializers.ValidationError("Аккаунт деактивирован")
        attrs["user"] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model  = CustomUser
        fields = ["id", "email", "first_name", "last_name", "full_name", "role", "created_at"]
        read_only_fields = ["id", "email", "role", "created_at"]

    def get_full_name(self, obj):
        return obj.full_name
