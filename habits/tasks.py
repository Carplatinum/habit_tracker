from celery import shared_task
from telegram_bot.tasks import send_telegram_message
from telegram_bot.models import TelegramUser
from .models import Habit
from django.utils import timezone
from datetime import timedelta


@shared_task
def cleanup_old_missed_habits():
    threshold_date = timezone.now() - timedelta(days=30)
    missed_habits = Habit.objects.filter(last_missed__lt=threshold_date)
    count = missed_habits.count()
    missed_habits.delete()
    return f"Deleted {count} old missed habits."


@shared_task
def send_habit_reminders():
    now = timezone.now()
    habits = Habit.objects.filter(
        time__hour=now.hour,
        time__minute=now.minute,
        is_public=False
    )
    for habit in habits:
        telegram_user = TelegramUser.objects.filter(user=habit.owner).first()
        if telegram_user and telegram_user.chat_id:
            message = (
                f"Напоминание о привычке: {habit.action} в {habit.place} "
                f"в {habit.time.strftime('%H:%M')}"
            )
            send_telegram_message.delay(telegram_user.chat_id, message)


@shared_task
def send_inactivity_reminders():
    threshold_date = timezone.now() - timedelta(days=3)
    inactive_users = set(
        Habit.objects.filter(last_done__lt=threshold_date).values_list('owner', flat=True)
    )
    for user_id in inactive_users:
        telegram_user = TelegramUser.objects.filter(user_id=user_id).first()
        if telegram_user and telegram_user.chat_id:
            message = "Мы заметили, что вы давно не выполняли привычку! Пора вернуться к здоровым привычкам."
            send_telegram_message.delay(telegram_user.chat_id, message)
