import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


app.conf.beat_schedule = {

    "test-every-10-seconds": {
        "task":     "notifications.tasks.test_periodic_task",
        "schedule": 10.0,
    },

    "daily-report-9am": {
        "task":     "notifications.tasks.send_daily_report",
        "schedule": crontab(hour=9, minute=0),
    },

    "weekly-digest-monday": {
        "task":     "notifications.tasks.send_weekly_digest",
        "schedule": crontab(hour=8, minute=0, day_of_week=1),
    },

    "clean-old-notifications": {
        "task":     "notifications.tasks.clean_old_notifications",
        "schedule": crontab(minute="*/30"),
    },
}

app.conf.timezone = "Asia/Bishkek"