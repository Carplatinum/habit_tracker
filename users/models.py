from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """Менеджер для CustomUser с email как username."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Требуется email')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser должен иметь is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser должен иметь is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None  # убираем поле username
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'  # используем email для логина
    REQUIRED_FIELDS = []  # убираем обязательное username

    objects = CustomUserManager()

    def __str__(self):
        return self.email
