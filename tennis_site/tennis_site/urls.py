"""
URL configuration for tennis_site project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from players.views import index  # главная страница

urlpatterns = [
    # Админка
    path("admin/", admin.site.urls),

    # Главная страница
    path("", index, name="index"),

    # Приложения
    path("players/", include("players.urls")),          # Игроки + профиль
    path("matches/", include("matches.urls")),          # Матчи
    path("chat/", include(("chat.urls", "chat"), namespace="chat")),  # Чат
    path("friends/", include("friends.urls")),          # Друзья
    path("users/", include("users.urls")),              # Пользователи
    path("tournaments/", include("tournaments.urls")),  # Турниры
    path("api/", include("api.urls")),                  # API
]

# Подключение статики и медиа (только при DEBUG = True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
