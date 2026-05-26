import logging

from celery.result import AsyncResult
from rest_framework import status
from rest_framework.permissions import  IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsAdminOrManager
from .models import Notification
from .tasks import (
    add_numbers,
    send_bulk_email,
    send_daily_report,
    send_email_notification
)

logger = logging.getLogger(__name__)

class TestCeleryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        task = add_numbers.delay(10, 25)
        return Response({
            "message": "Задача поставлена",
            "task_id": task.id,
        })

class TaskStatusView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, task_id):
        result = AsyncResult(task_id)
        return Response({
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready else None
        })

class SendEmailView(APIView):
    permission_classes = [IsAdminOrManager]

    def post(self, request):
        user_id = request.data.get("user_id")
        subject = request.data.get("subject")
        message = request.data.get("message")

        if not all([user_id, subject,message]):
            return Response(
                {"error": "user_id, subject и message обязательны"},
                status=status.HTTP_400_BAD_REQUEST
            )

        task = send_email_notification.delay(user_id, subject, message)

        return Response({
            "message": "Письмо поставлено в очередь",
            "task_id": task.id,
        }, status=status.HTTP_202_ACCEPTED)

class SendBulkEmailView(APIView):
    permission_classes = [IsAdminOrManager]

    def post(self, request):
        subject = request.data.get("subject")
        message = request.data.get("message")
        role    = request.data.get("role")

        if not all([subject, message]):
            return Response(
                {"error": "subject и message обязательны"},
                status=status.HTTP_400_BAD_REQUEST
            )

        task = send_bulk_email.delay(subject, message, role)

        return Response({
            "message": "Рассылка запущена",
            "task_id": task.id,
            "role": role or "all"
        }, status=status.HTTP_202_ACCEPTED)

class SendDailyReportView(APIView):
    permission_classes = [IsAdminOrManager]

    def post(self, request):
        task = send_daily_report.delay()
        return Response({
            "message": "Отчёт поставлено в очередь",
            "task_id": task.id,
        }, status=status.HTTP_202_ACCEPTED)

class MyNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(
            user=request.user,
        ).values(
            "id", "type", "title", "message",
            "status", "created_at", "sent_at",
        )
        return Response(list(notifications))
