import requests
from django.conf import settings
from rest_framework.exceptions import ValidationError


class GoogleOAuthService:
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"

    @classmethod
    def get_auth_url(cls) -> str:
        scopes = " ".join(settings.GOOGLE_SCOPES)
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": scopes,
            "access_type": "offline",
            "prompt": "consent",
        }

        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{cls.AUTH_URL}?{query_string}"

    @classmethod
    def exchange_code_for_token(cls, code: str) -> str:
        payload = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        response = requests.post(cls.TOKEN_URL, data=payload)

        if response.status_code != 200:
            raise ValidationError(
                f"Ошибка получения токена от Google: {response.json()}"
            )

        token_data = response.json()

        if "error" in token_data:
            raise ValidationError(f"Google вернул ошибку: {token_data['error']}")

        return token_data["access_token"]

    @classmethod
    def get_user_info(cls, access_token: str) -> dict:
        response = requests.get(
            cls.USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code != 200:
            raise ValidationError("Не удалось получить данные пользователя от Google")

        return response.json()

    @classmethod
    def get_google_user_data(cls, code: str) -> dict:
        access_token = cls.exchange_code_for_token(code)
        user_info = cls.get_user_info(access_token)
        return user_info