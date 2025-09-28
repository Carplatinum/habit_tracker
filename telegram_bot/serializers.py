from rest_framework import serializers
from .models import TelegramUser


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ['id', 'user', 'chat_id']
        read_only_fields = ['user']

    def create(self, validated_data):
        user = self.context['request'].user
        telegram_user, created = TelegramUser.objects.update_or_create(
            user=user, defaults={'chat_id': validated_data['chat_id']}
        )
        return telegram_user
