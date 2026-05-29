from .base import *

DEBUG = False

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

DATABASES = {
    "default": {
        "ENGINE":   "django.db.backends.postgresql",
        "NAME":     os.getenv("POSTGRES_DB"),
        "USER":     os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST":     os.getenv("POSTGRES_HOST", "db"),
        "PORT":     os.getenv("POSTGRES_PORT", "5432"),
    }
}

SECURE_PROXY_SSL_HEADER  = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT      = False
SESSION_COOKIE_SECURE    = True
CSRF_COOKIE_SECURE       = True

LOGGING = {
    "version":            1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style":  "{",
        },
    },
    "handlers": {
        "file": {
            "level":     "ERROR",
            "class":     "logging.FileHandler",
            "filename":  BASE_DIR / "logs/errors.log",
            "formatter": "verbose",
        },
        "console": {
            "class":     "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level":    "INFO",
    },
}
