from django.urls import path
from . import views

urlpatterns = [
    # Профиль текущего пользователя
    path("profile/create/", views.create_player_profile, name="player_create_profile"),
    path("profile/edit/", views.edit_my_player_profile, name="player_profile_edit"),
    path("profile/me/", views.my_profile, name="my_profile"),

    # Список и CRUD игроков
    path("", views.PlayerListView.as_view(), name="players_list"),
    path("add/", views.PlayerCreateView.as_view(), name="player_add"),
    path("<int:pk>/", views.PlayerDetailView.as_view(), name="player_detail"),
    path("<int:pk>/edit/", views.PlayerUpdateView.as_view(), name="player_edit"),
    path("<int:pk>/delete/", views.PlayerDeleteView.as_view(), name="player_delete"),

    # Достижения
    path("<int:pk>/achievements/add/", views.add_achievement, name="add_achievement"),
    path("achievements/<int:pk>/edit/", views.edit_achievement, name="edit_achievement"),
    path("achievements/<int:pk>/delete/", views.delete_achievement, name="delete_achievement"),
]
