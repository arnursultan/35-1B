from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model            = CustomUser
    list_display     = ["email", "full_name", "role", "is_staff", "is_active"]
    list_filter      = ["role", "is_staff", "is_active"]
    ordering         = ["email"]
    search_fields    = ["email", "first_name", "last_name"]

    fieldsets = (
        (None,           {"fields": ("email", "password")}),
        ("Личные данные", {"fields": ("first_name", "last_name", "role")}),
        ("Права доступа", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields":  ("email", "password1", "password2", "role", "is_staff", "is_active"),
        }),
    )
