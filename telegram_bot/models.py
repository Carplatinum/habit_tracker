from django.db import models
from django.conf import settings


class TelegramUser(models.Model):
    """
    Модель пользователя Telegram, связанная с пользователем Django.
    Хранит chat_id для общения с ботом.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Пользователь Django'
    )
    chat_id = models.CharField(max_length=50, unique=True, verbose_name='ID чата Telegram')

    def __str__(self):
        if self.user:
            return f'TelegramUser {self.chat_id} для {self.user.email}'
        return f'TelegramUser {self.chat_id}'
