from django.urls import path
from . import views

app_name = "tournaments"

urlpatterns = [
    # Список и CRUD
    path("", views.tournaments_list, name="tournaments_list"),
    path("add/", views.TournamentCreateView.as_view(), name="tournament_add"),
    path("<int:pk>/", views.TournamentDetailView.as_view(), name="tournament_detail"),
    path("<int:pk>/edit/", views.TournamentUpdateView.as_view(), name="tournament_edit"),
    path("<int:pk>/delete/", views.TournamentDeleteView.as_view(), name="tournament_delete"),

    # Участие
    path("<int:pk>/join/", views.tournament_join, name="tournament_join"),
    path("<int:pk>/leave/", views.tournament_leave, name="tournament_leave"),

    # Генерация стадий (актуальные имена)
    path("<int:pk>/generate/groups/", views.tournament_generate_groups_anytime,
         name="tournament_generate_groups_anytime"),
    path("<int:pk>/generate/bracket/", views.tournament_generate_knockout_any,
         name="tournament_generate_knockout_any"),

    # Алиасы под старые имена (на случай старых ссылок)
    path("<int:pk>/generate/ko/", views.tournament_generate_knockout_any,
         name="tournament_generate_bracket_anytime"),
    path("<int:pk>/generate/grp/", views.tournament_generate_groups_anytime,
         name="tournament_generate_groups_any"),

    # Группы/плей-офф: детали и счёт
    path("groups/<int:pk>/", views.group_detail, name="group_detail"),
    path("groups/match/<int:match_id>/score/", views.group_set_score, name="group_set_score"),
    path("bracket/match/<int:match_id>/score/", views.bracket_set_score, name="bracket_set_score"),
]
