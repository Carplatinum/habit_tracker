import os
import django
import logging
from asgiref.sync import sync_to_async
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    ConversationHandler, MessageHandler, filters
)
from telegram import Update
from django.core.management.base import BaseCommand
from telegram_bot.models import TelegramUser, Habit, HabitRecord
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

User = get_user_model()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

HABIT_NAME = 1


async def get_django_user_by_chat_id(chat_id):
    """Получить пользователя Django по chat_id Telegram."""
    try:
        tg_user = await sync_to_async(TelegramUser.objects.get)(chat_id=str(chat_id))
        return tg_user.user
    except TelegramUser.DoesNotExist:
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /start: приветствие и список команд."""
    logger.info(f"/start команда от {update.effective_user.username}")
    await update.message.reply_text(
        "Привет! Я ваш Habit Tracker бот.\n"
        "Доступные команды:\n"
        "/register - регистрация\n"
        "/add или /new_habit - добавить привычку\n"
        "/habits - список привычек\n"
        "/done <id> - пометить выполнение\n"
        "/fail <id> - пометить невыполнение\n"
        "/delete <id> - удалить привычку\n"
        "/stats <id> - статистика привычки\n"
        "/cancel - отмена"
    )


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /register: регистрация пользователя и привязка к chat_id."""
    chat_id = update.effective_chat.id
    user = update.effective_user

    django_user = None
    try:
        django_user = await sync_to_async(User.objects.get)(email=user.username)
    except User.DoesNotExist:
        django_user = None

    tg_user, created = await sync_to_async(TelegramUser.objects.get_or_create)(
        chat_id=str(chat_id)
    )
    if django_user and tg_user.user != django_user:
        tg_user.user = django_user
        await sync_to_async(tg_user.save)()

    if created:
        await update.message.reply_text("Вы успешно зарегистрированы в Habit Tracker!")
    else:
        await update.message.reply_text("Вы уже зарегистрированы.")


async def add_habit_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало диалога для добавления новой привычки."""
    await update.message.reply_text("Введите название привычки:")
    return HABIT_NAME


async def add_habit_name_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка названия и создание новой привычки в базе."""
    habit_name = update.message.text.strip()
    django_user = await get_django_user_by_chat_id(update.effective_chat.id)
    if not django_user:
        await update.message.reply_text("Вы не зарегистрированы. Используйте /register.")
        return ConversationHandler.END

    habit = await sync_to_async(Habit.objects.create)(user=django_user, name=habit_name)
    await update.message.reply_text(f"Привычка '{habit.name}' добавлена с ID {habit.id}")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена текущего разговора."""
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END


async def habits_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /habits: показать список привычек пользователя."""
    django_user = await get_django_user_by_chat_id(update.effective_chat.id)
    if not django_user:
        await update.message.reply_text("Вы не зарегистрированы. Используйте /register.")
        return

    habits = await sync_to_async(list)(Habit.objects.filter(user=django_user))
    if not habits:
        await update.message.reply_text("Привычек пока нет, добавьте через /add.")
        return

    msg = "Ваши привычки:\n" + "\n".join(f"{h.id}: {h.name}" for h in habits)
    await update.message.reply_text(msg)


async def habit_mark(update: Update, context: ContextTypes.DEFAULT_TYPE, done: bool) -> None:
    """Общая функция для отметки привычки выполненной или невыполненной."""
    django_user = await get_django_user_by_chat_id(update.effective_chat.id)
    if not django_user:
        await update.message.reply_text("Вы не зарегистрированы. Используйте /register.")
        return

    if not context.args:
        await update.message.reply_text("Укажите ID привычки, например /done 1")
        return

    try:
        habit = await sync_to_async(Habit.objects.get)(id=context.args[0], user=django_user)
    except Habit.DoesNotExist:
        await update.message.reply_text("Привычка с таким ID не найдена.")
        return

    from datetime import date
    today = date.today()
    record, created = await sync_to_async(HabitRecord.objects.get_or_create)(
        habit=habit, date=today, defaults={'completed': done}
    )
    if not created:
        record.completed = done
        await sync_to_async(record.save)()

    status = 'выполнена' if done else 'не выполнена'
    await update.message.reply_text(f"Привычка '{habit.name}' за сегодня помечена как {status}.")


async def habit_mark_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отметить привычку выполненной."""
    await habit_mark(update, context, done=True)


async def habit_mark_fail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отметить привычку невыполненной."""
    await habit_mark(update, context, done=False)


async def habit_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Удалить привычку по ID."""
    django_user = await get_django_user_by_chat_id(update.effective_chat.id)
    if not django_user:
        await update.message.reply_text("Вы не зарегистрированы. Используйте /register.")
        return
    if not context.args:
        await update.message.reply_text("Укажите ID привычки для удаления.")
        return
    try:
        habit = await sync_to_async(Habit.objects.get)(id=context.args[0], user=django_user)
    except Habit.DoesNotExist:
        await update.message.reply_text("Привычка не найдена.")
        return
    await sync_to_async(habit.delete)()
    await update.message.reply_text(f"Привычка '{habit.name}' удалена.")


async def habit_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать статистику выполнения привычки."""
    django_user = await get_django_user_by_chat_id(update.effective_chat.id)
    if not django_user:
        await update.message.reply_text("Вы не зарегистрированы. Используйте /register.")
        return
    if not context.args:
        await update.message.reply_text("Укажите ID привычки для просмотра статистики.")
        return
    try:
        habit = await sync_to_async(Habit.objects.get)(id=context.args[0], user=django_user)
    except Habit.DoesNotExist:
        await update.message.reply_text("Привычка не найдена.")
        return
    records = await sync_to_async(list)(HabitRecord.objects.filter(habit=habit).order_by('date'))
    total_days = len(records)
    completed_days = sum(1 for r in records if r.completed)
    percent = (completed_days / total_days * 100) if total_days > 0 else 0
    await update.message.reply_text(
        f"Статистика по привычке '{habit.name}':\n"
        f"Всего дней: {total_days}\n"
        f"Выполнено: {completed_days}\n"
        f"Процент выполнения: {percent:.1f}%"
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок бота: логирует ошибку и уведомляет пользователя."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if update and hasattr(update, "message") and update.message:
        await update.message.reply_text("Произошла внутренняя ошибка. Администратор уведомлен.")


class Command(BaseCommand):
    help = 'Запуск Telegram бота Habit Tracker'

    def handle(self, *args, **kwargs):
        logger.info("Запуск Telegram бота...")
        application = ApplicationBuilder().token(TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("register", register))
        conversation_handler = ConversationHandler(
            entry_points=[CommandHandler("add", add_habit_start), CommandHandler("new_habit", add_habit_start)],
            states={
                HABIT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_habit_name_received)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
        application.add_handler(conversation_handler)
        application.add_handler(CommandHandler("habits", habits_list))
        application.add_handler(CommandHandler("done", habit_mark_done))
        application.add_handler(CommandHandler("fail", habit_mark_fail))
        application.add_handler(CommandHandler("delete", habit_delete))
        application.add_handler(CommandHandler("stats", habit_stats))

        application.add_error_handler(error_handler)

        self.stdout.write(self.style.SUCCESS("Бот запущен"))
        application.run_polling()
