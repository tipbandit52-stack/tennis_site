from django.urls import path
from . import views

urlpatterns = [
    path("", views.friends_list, name="friends_list"),

    # Отправить заявку (из профиля игрока) — POST
    path("add/<int:user_id>/", views.send_friend_request, name="send_friend_request"),

    # Входящие заявки
    path("accept/<int:pk>/", views.accept_friend, name="accept_friend"),
    path("reject/<int:pk>/", views.reject_friend, name="reject_friend"),

    # Исходящие заявки — отмена
    path("cancel/<int:pk>/", views.cancel_request, name="cancel_request"),

    # Удаление уже существующей дружбы
    path("remove/<int:pk>/", views.remove_friend, name="remove_friend"),
]
