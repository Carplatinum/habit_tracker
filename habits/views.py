from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.http import HttpResponse

from .models import Habit
from .serializers import HabitSerializer
from .permissions import IsOwnerOrReadOnly


def index(request):
    return HttpResponse("Добро пожаловать на Habit Tracker!")


class HabitPagination(PageNumberPagination):
    page_size = 5  # Пагинация по 5 привычек на страницу


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        # Возвращаем привычки пользователя и публичные
        return Habit.objects.filter(Q(owner=user) | Q(is_public=True)).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
