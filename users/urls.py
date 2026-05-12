from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, LogoutView, ProfileView, RegisterView, ChangePasswordView

urlpatterns = [
    path("register/",       RegisterView.as_view(),         name="register"),
    path("login/",          LoginView.as_view(),            name="login"),
    path("logout/",         LogoutView.as_view(),           name="logout"),
    path("token/refresh/",  TokenRefreshView.as_view(),     name="token-refresh"),
    path("me/",             ProfileView.as_view(),          name="profile"),
    path("me/password/",    ChangePasswordView.as_view(),   name="change_password")
]

# SCOPE - разрешения
#
# client_id - ID нашего приложения
# client_secret - секрет приложения, ключ
#
# code - временный код от Google
# access token - токен Гугл для получения данных юзера
# redirect uri - куда Гугл вернёт юзера после логина
#
