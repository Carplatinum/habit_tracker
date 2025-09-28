from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterUserViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/users/register/"

    def test_register_valid_user(self):
        data = {
            "email": "apiuser@example.com",
            "password": "Str0ngPassw0rd!"
        }
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == 201
        assert User.objects.filter(email="apiuser@example.com").exists()

    def test_register_invalid_password(self):
        data = {
            "email": "apiuser2@example.com",
            "password": "123"
        }
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == 400
        assert 'password' in response.data
