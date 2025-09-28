import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Логирование конфигурация
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_REGISTER_URL = "http://localhost:8000/api/telegram/register/"
USER_JWT_TOKEN = os.getenv('DJANGO_USER_JWT_TOKEN')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"/start команда от {update.effective_user.username}")
    await update.message.reply_text(
        "Привет! Чтобы получать напоминания, зарегистрируйте ваш чат командой /register."
    )


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"/register команда от {update.effective_user.username}")
    chat_id = update.effective_chat.id

    safe_token = USER_JWT_TOKEN.encode('ascii', 'ignore').decode('ascii')
    headers = {
        "Authorization": f"Bearer {safe_token}",
        "Content-Type": "application/json"
    }
    data = {"chat_id": str(chat_id)}

    try:
        response = requests.post(API_REGISTER_URL, json=data, headers=headers)
        if response.status_code == 201:
            await update.message.reply_text("Ваш чат успешно зарегистрирован для получения напоминаний!")
        elif response.status_code == 400:
            await update.message.reply_text("Ошибка регистрации: неверные данные.")
        else:
            await update.message.reply_text(f"Ошибка регистрации с кодом {response.status_code}")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Сетевая ошибка при регистрации: {e}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Стартовое сообщение\n/register - Зарегистрировать чат\n/help - Помощь"
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Ошибка при обработке обновления:", exc_info=context.error)
    if update and hasattr(update, "message") and update.message:
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")


def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("help", help_command))
    application.add_error_handler(error_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
