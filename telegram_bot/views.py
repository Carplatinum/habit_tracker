from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import TelegramUserSerializer


class TelegramUserRegisterView(generics.CreateAPIView):
    serializer_class = TelegramUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception:
            return Response({"detail": "Ошибка создания Telegram пользователя."}, status=status.HTTP_400_BAD_REQUEST)
