from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Habit(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='habits',
        verbose_name='Пользователь'
    )
    place = models.CharField(max_length=255, verbose_name='Место')
    time = models.TimeField(verbose_name='Время')
    action = models.CharField(max_length=255, verbose_name='Действие')
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name='Признак приятной привычки',
        help_text='Если True — это приятная привычка, иначе полезная'
    )
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'is_pleasant': True},
        verbose_name='Связанная привычка',
        help_text='Для полезной привычки — связанная приятная привычка'
    )
    periodicity = models.PositiveIntegerField(
        default=1,
        verbose_name='Периодичность (в днях)',
        help_text='Периодичность напоминания, минимум 1, максимум 7'
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Вознаграждение',
        help_text='Чем пользователь вознаградит себя'
    )
    duration_seconds = models.PositiveIntegerField(
        verbose_name='Время на выполнение (сек)',
        help_text='Время, которое займет привычка (макс. 120 сек)'
    )
    is_public = models.BooleanField(default=False, verbose_name='Публичная привычка')

    def clean(self):
        # Нельзя одновременно иметь и вознаграждение и связанную привычку
        if self.reward and self.related_habit:
            raise ValidationError('Одновременно нельзя указать вознаграждение и связанную привычку.')

        # У приятной привычки не может быть вознаграждения и связанной привычки
        if self.is_pleasant and (self.reward or self.related_habit):
            raise ValidationError('У приятной привычки не может быть вознаграждения или связанной привычки.')

        # Время выполнения не больше 120 секунд
        if self.duration_seconds > 120:
            raise ValidationError('Время выполнения не может быть больше 120 секунд.')

        # Периодичность от 1 до 7 дней
        if self.periodicity < 1 or self.periodicity > 7:
            raise ValidationError('Периодичность должна быть от 1 до 7 дней.')

    def __str__(self):
        return f'{self.action} в {self.time} в {self.place}'

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['time']
