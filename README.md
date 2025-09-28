# Habit Tracker

Проект Habit Tracker — это SPA веб-приложение для трекинга полезных привычек с интеграцией Telegram для напоминаний и оповещений.

## Описание

- Реализован бэкенд на Django и Django REST Framework
- Кастомная модель пользователя с email для аутентификации
- Модель привычек с валидацией периодичности, времени, вознаграждений
- Пагинация привычек по 5 на страницу
- Интеграция с Telegram-ботом для регистрации чат-идентификаторов и рассылок через Celery
- Отложенные задачи Celery с Redis брокером и celery-beat для расписаний

## Технологии

- Python 3.13, Django 5.x, Django REST Framework
- Celery + Redis + django-celery-beat
- PostgreSQL
- python-telegram-bot для бота Telegram
- Poetry для управления зависимостями

## Установка и запуск

1. Клонировать репозиторий
2. Установить Poetry: https://python-poetry.org/docs/
3. Установить зависимости:

    ```
    poetry install
    ```
4. Создать `.env` файл на основе примера `.env.example` и заполнить переменные окружения
5. Подготовить базу данных и применить миграции:

    ```
    python manage.py migrate
    ```
6. Запустить Redis сервер (требуется для Celery)
7. Запустить Celery worker и beat в отдельных терминалах:

    ```
    celery -A config worker --loglevel=info
    celery -A config beat --loglevel=info
    ```
8. Запустить Django сервер:

    ```
    python manage.py runserver
    ```
9. Запустить Telegram бота (если нужно):

    ```
    python manage.py start_bot
    ```

## API

- Регистрация пользователей: `/api/users/register/`
- Авторизация и получение JWT: `/api/users/login/`
- CRUD привычек: `/api/habits/`
- Регистрация Telegram чата: `/api/telegram/register/`

## Тесты

- Запуск всех тестов:

    ```
    python manage.py test
    ```

## Конфигурация

- Все секреты и параметры в `.env`
- Telegram токен через `TELEGRAM_BOT_TOKEN`
- База данных — PostgreSQL с параметрами из `.env`
- Redis для Celery через `CELERY_BROKER_URL` и `CELERY_RESULT_BACKEND`
