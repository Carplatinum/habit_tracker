from django.urls import path
from .views import TelegramUserRegisterView

urlpatterns = [
    path('register/', TelegramUserRegisterView.as_view(), name='telegram_user_register'),
]
