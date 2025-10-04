from django.urls import path
from . import views

app_name = "chat"  # <--- ДОБАВИЛ namespace

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("<int:player_id>/", views.chat_with, name="chat_with"),
    path("<int:chat_id>/delete/", views.delete_chat, name="delete_chat"),

    # API
    path("api/send/<int:chat_id>/", views.api_send, name="api_send"),
    path("api/messages/<int:chat_id>/", views.api_messages, name="api_messages"),
    path("api/mark_read/<int:chat_id>/", views.api_mark_read, name="api_mark_read"),
    path("api/unread_count/", views.api_unread_count, name="api_unread_count"),
    path("api/unread_per_chat/", views.api_unread_per_chat, name="api_unread_per_chat"),
    path("<int:chat_id>/delete/", views.delete_chat, name="delete_chat"),
]
