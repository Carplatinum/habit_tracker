from django.contrib import admin
from habits.views import index
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/habits/', include('habits.urls')),
    path('api/users/', include('users.urls')),
    path('api/telegram/', include('telegram_bot.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('', index, name='index'),
]
