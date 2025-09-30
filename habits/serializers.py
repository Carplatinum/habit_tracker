from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = [
            'id',
            'owner',
            'place',
            'time',
            'action',
            'is_pleasant',
            'related_habit',
            'periodicity',
            'reward',
            'duration_seconds',
            'is_public',
            'last_missed',
            'last_done',
        ]
        read_only_fields = ['owner']

    def validate_periodicity(self, value):
        if not (1 <= value <= 7):
            raise serializers.ValidationError("Периодичность должна быть от 1 до 7 дней.")
        return value

    def validate(self, data):
        reward = data.get('reward')
        related_habit = data.get('related_habit')
        is_pleasant = data.get('is_pleasant', False)

        if reward and related_habit:
            raise serializers.ValidationError("Одновременно нельзя указать вознаграждение и связанную привычку.")
        if is_pleasant and (reward or related_habit):
            raise serializers.ValidationError("У приятной привычки не может быть вознаграждения или связанной привычки.")

        if related_habit and not Habit.objects.filter(pk=related_habit.pk, is_pleasant=True).exists():
            raise serializers.ValidationError("Связанная привычка должна быть приятной и существовать.")

        duration_seconds = data.get('duration_seconds')
        if duration_seconds and duration_seconds > 120:
            raise serializers.ValidationError("Время выполнения не может быть больше 120 секунд.")

        return data
