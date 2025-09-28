import os
import logging
from celery import shared_task
from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_telegram_message(self, chat_id, text):
    """
    Задача Celery для отправки сообщения пользователю Telegram через Bot API.

    Параметры:
    - chat_id: ID чата в Telegram (string или int).
    - text: текст сообщения.

    Логирует ошибки и пытается сделать 3 попытки при сбое.
    """
    bot = Bot(token=TELEGRAM_TOKEN)
    try:
        bot.send_message(chat_id=chat_id, text=text)
        logger.info(f"Message sent to chat_id={chat_id}")
    except TelegramError as exc:
        logger.error(f"TelegramError while sending message to {chat_id}: {exc}")
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for chat_id={chat_id}")
    except Exception as exc:
        logger.exception(f"Unexpected error in send_telegram_message for chat_id={chat_id}: {exc}")
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for chat_id={chat_id} due to unexpected error")
