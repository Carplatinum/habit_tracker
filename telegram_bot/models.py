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


class Habit(models.Model):
    """
    Модель привычки пользователя.
    Каждая привычка принадлежит одному пользователю (user).
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    name = models.CharField(max_length=255, verbose_name='Название привычки')

    def __str__(self):
        return self.name


class HabitRecord(models.Model):
    """
    Отметка выполнения привычки за конкретный день.
    Связывается с Habit.
    """
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, verbose_name='Привычка')
    date = models.DateField(verbose_name='Дата')
    completed = models.BooleanField(default=False, verbose_name='Выполнено')

    class Meta:
        unique_together = ('habit', 'date')
        verbose_name = 'Отметка привычки'
        verbose_name_plural = 'Отметки привычек'

    def __str__(self):
        status = 'Выполнено' if self.completed else 'Не выполнено'
        return f"{self.habit.name} - {self.date}: {status}"
