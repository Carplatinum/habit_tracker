from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch
from telegram_bot.models import TelegramUser

User = get_user_model()


class TelegramUserRegisterViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="pass")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = '/api/telegram/register/'

    def test_register_telegram_user(self):
        data = {"chat_id": "987654321"}
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == 201
        assert TelegramUser.objects.filter(user=self.user, chat_id="987654321").exists()

    @patch('telegram_bot.serializers.TelegramUserSerializer.create')
    def test_register_failure(self, mock_create):
        mock_create.side_effect = Exception("Ошибка создания")
        data = {"chat_id": "987654321"}
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == 400
