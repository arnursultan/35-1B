from django.urls import path
from .views import (
    MyNotificationsView,
    SendBulkEmailView,
    SendDailyReportView,
    SendEmailView,
    TaskStatusView,
    TestCeleryView
)

urlpatterns = [
    path("test/",               TestCeleryView.as_view(),       name="test-celery"),
    path("task/<str:task_id>/", TaskStatusView.as_view(),       name="task-status"),
    path("send-email",          SendEmailView.as_view(),        name="send-email"),
    path("send-bulk-email",     SendBulkEmailView.as_view(),    name="send-bulk-email"),
    path("send-report",         SendDailyReportView.as_view(),  name="send-report"),
    path("my/",                 MyNotificationsView.as_view(),  name="my-notifications"),
]