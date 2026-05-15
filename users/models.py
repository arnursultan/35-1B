from urllib.parse import uses_query

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        ADMIN   = "admin",   "Администратор"
        MANAGER = "manager", "Менеджер"
        CLIENT  = "client",  "Клиент"

    email      = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name  = models.CharField(max_length=50, blank=True)
    role       = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT)

    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    avatar = models.URLField(blank=True, null=True)
    
    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects    = CustomUserManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name        = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.email} [{self.role}]"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
