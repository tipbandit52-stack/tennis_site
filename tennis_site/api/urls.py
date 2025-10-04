from django.urls import path
from . import views

urlpatterns = [
    # Игроки
    path("players/", views.players_list, name="players_list_api"),
    path("players/<int:id>/", views.player_detail, name="player_detail_api"),

    # Матчи
    path("matches/", views.matches_list, name="matches_list_api"),
    path("matches/<int:id>/", views.match_detail, name="match_detail_api"),

    # Турниры
    path("tournaments/", views.tournaments_list, name="tournaments_list_api"),
    path("tournaments/<int:id>/", views.tournament_detail, name="tournament_detail_api"),
]
