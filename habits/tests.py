from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from datetime import time
from .models import Habit
from .serializers import HabitSerializer

User = get_user_model()


class HabitSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="password")
        self.pleasant_habit = Habit.objects.create(
            owner=self.user,
            place="дома",
            time=time(7, 0),
            action="приятная привычка",
            is_pleasant=True,
            periodicity=1,
            duration_seconds=60,
            is_public=False,
        )

    def serializer_data(self, **kwargs):
        data = {
            "place": "дома",
            "time": time(7, 0).isoformat(),
            "action": "зарядка",
            "is_pleasant": kwargs.get("is_pleasant", False),
            "related_habit": kwargs.get("related_habit", None),
            "periodicity": kwargs.get("periodicity", 3),
            "reward": kwargs.get("reward", ""),
            "duration_seconds": kwargs.get("duration_seconds", 60),
            "is_public": kwargs.get("is_public", False),
        }
        if isinstance(data.get("related_habit"), Habit):
            data["related_habit"] = data["related_habit"].id
        return data

    def test_periodicity_bounds(self):
        data = self.serializer_data(periodicity=0)
        serializer = HabitSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors or "periodicity" in serializer.errors

        data = self.serializer_data(periodicity=8)
        serializer = HabitSerializer(data=data)
        assert not serializer.is_valid()

    def test_reward_and_related_habit_exclusive(self):
        data = self.serializer_data(reward="похвала", related_habit=self.pleasant_habit)
        serializer = HabitSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors or "reward" in serializer.errors
