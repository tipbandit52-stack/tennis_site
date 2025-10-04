from django.urls import path
from django.http import HttpResponse
from . import views

def not_implemented(request, *args, **kwargs):
    return HttpResponse("Страница пока не реализована (URL есть, но view отсутствует).", status=501)

urlpatterns = []

# Список
if hasattr(views, "match_list"):
    urlpatterns.append(path("", views.match_list, name="match_list"))
else:
    urlpatterns.append(path("", not_implemented, name="match_list"))

# Создание
if hasattr(views, "match_add"):
    urlpatterns.append(path("add/", views.match_add, name="match_add"))
elif hasattr(views, "MatchCreateView"):
    urlpatterns.append(path("add/", views.MatchCreateView.as_view(), name="match_add"))
else:
    urlpatterns.append(path("add/", not_implemented, name="match_add"))

# Детальная
if hasattr(views, "match_detail"):
    urlpatterns.append(path("<int:pk>/", views.match_detail, name="match_detail"))
elif hasattr(views, "MatchDetailView"):
    urlpatterns.append(path("<int:pk>/", views.MatchDetailView.as_view(), name="match_detail"))
else:
    urlpatterns.append(path("<int:pk>/", not_implemented, name="match_detail"))

# Редактирование
if hasattr(views, "match_edit"):
    urlpatterns.append(path("<int:pk>/edit/", views.match_edit, name="match_edit"))
elif hasattr(views, "MatchUpdateView"):
    urlpatterns.append(path("<int:pk>/edit/", views.MatchUpdateView.as_view(), name="match_edit"))
else:
    urlpatterns.append(path("<int:pk>/edit/", not_implemented, name="match_edit"))

# Удаление
if hasattr(views, "match_delete"):
    urlpatterns.append(path("<int:pk>/delete/", views.match_delete, name="match_delete"))
elif hasattr(views, "MatchDeleteView"):
    urlpatterns.append(path("<int:pk>/delete/", views.MatchDeleteView.as_view(), name="match_delete"))
else:
    urlpatterns.append(path("<int:pk>/delete/", not_implemented, name="match_delete"))

# Присоединиться
if hasattr(views, "join_match"):
    urlpatterns.append(path("<int:pk>/join/", views.join_match, name="join_match"))
else:
    urlpatterns.append(path("<int:pk>/join/", not_implemented, name="join_match"))

# Выйти из матча
if hasattr(views, "leave_match"):
    urlpatterns.append(path("<int:pk>/leave/", views.leave_match, name="leave_match"))
else:
    urlpatterns.append(path("<int:pk>/leave/", not_implemented, name="leave_match"))
