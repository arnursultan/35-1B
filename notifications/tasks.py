import logging

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail, send_mass_mail
from django.utils import timezone

from .models import Notification


logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def add_numbers(a, b):
    result = a + b
    logger.info(f"add_numbers: {a} + {b} = {result}")
    return result


@shared_task(bind=True, max_retries=3)
def send_email_notification(self, user_id: int, subject: str, message: str):
    notification = None

    try:
        user = User.objects.get(id=user_id)

        notification = Notification.objects.create(
            user=user,
            type=Notification.Type.EMAIL,
            title=subject,
            message=message,
            status=Notification.Status.PENDING,
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        notification.status = Notification.Status.SENT
        notification.sent_at = timezone.now()
        notification.save()

        logger.info(f"Письмо отправлено → {user.email}")

        return {
            "status": "sent",
            "to": user.email,
        }

    except User.DoesNotExist:
        logger.error(f"Юзер {user_id} не найден")

        return {
            "status": "error",
            "message": "Юзер не найден",
        }

    except Exception as exc:
        logger.error(f"Ошибка отправки письма: {exc}")

        if notification:
            notification.status = Notification.Status.FAILED
            notification.save()

        raise self.retry(exc=exc, countdown=10)


@shared_task
def send_welcome_email(user_id: int):
    try:
        user = User.objects.get(id=user_id)

        subject = "Добро пожаловать!"

        message = (
            f"Привет, {user.first_name or user.email}!\n\n"
            f"Вы успешно зарегистрировались.\n"
            f"Ваша роль: {user.role}\n\n"
            f"С уважением,\n"
            f"Команда сервиса 35-1B"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        logger.info(f"Welcome email отправлен → {user.email}")

        return {
            "status": "sent",
            "to": user.email,
        }

    except User.DoesNotExist:
        logger.error(f"Юзер {user_id} не найден")

        return {
            "status": "error",
            "message": "Юзер не найден",
        }

    except Exception as exc:
        logger.error(f"Ошибка welcome email: {exc}")

        return {
            "status": "error",
            "message": str(exc),
        }


@shared_task
def send_bulk_email(subject: str, message: str, role: str = None):
    users = User.objects.filter(is_active=True)

    if role:
        users = users.filter(role=role)

    if not users.exists():
        return {
            "status": "no_users",
        }

    emails = tuple(
        (
            subject,
            f"Привет, {u.first_name or u.email}!\n\n{message}",
            settings.DEFAULT_FROM_EMAIL,
            [u.email],
        )
        for u in users
    )

    try:
        sent = send_mass_mail(emails, fail_silently=False)

        logger.info(f"Массовая рассылка: отправлено {sent} писем")

        return {
            "status": "sent",
            "count": sent,
        }

    except Exception as exc:
        logger.error(f"Ошибка массовой рассылки: {exc}")

        return {
            "status": "error",
            "message": str(exc),
        }


@shared_task
def send_daily_report():
    admins = User.objects.filter(role="admin", is_active=True)

    if not admins.exists():
        return {
            "status": "no_admins",
        }

    today = timezone.now().date()

    user_count = User.objects.filter(
        created_at__date=today
    ).count()

    subject = f"Ежедневный отчёт - {today}"

    message = (
        f"Отчёт за {today}\n"
        f"{'-' * 30}\n"
        f"Новых пользователей: {user_count}\n\n"
        f"С уважением,\n"
        f"Система"
    )

    emails = tuple(
        (
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [admin.email],
        )
        for admin in admins
    )

    send_mass_mail(
        emails,
        fail_silently=True,
    )

    logger.info(
        f"Отчёт отправлен {admins.count()} администраторам"
    )

    return {
        "date": str(today),
        "admins": admins.count(),
    }