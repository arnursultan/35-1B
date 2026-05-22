from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        EMAIL   = "email",   "Email"
        SYSTEM  = "system",  "Системное"
        REPORT  = "report",  "Отчёт"

    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает"
        SENT    = "sent",    "Отправлено"
        FAILED  = "failed",  "Ошибка"

    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True, blank=True
    )
    type       = models.CharField(max_length=20, choices=Type.choices)
    title      = models.CharField(max_length=255)
    message    = models.TextField()
    status     = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at    = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name        = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.type} → {self.title} [{self.status}]"
