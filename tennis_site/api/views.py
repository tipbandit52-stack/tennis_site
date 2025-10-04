from django.http import JsonResponse, Http404
from django.conf import settings
from players.models import Player
from matches.models import Match
from tournaments.models import Tournament


# ===== Вспомогательная проверка =====
def check_access(request):
    """
    Доступ разрешён если:
    1. Пользователь авторизован
    2. Либо передан правильный API ключ
    """
    if request.user.is_authenticated:
        return True

    api_key = request.headers.get("X-API-Key") or request.GET.get("api_key")
    if api_key == settings.UNIVERSAL_API_KEY:
        return True

    return False


# ===== Игроки =====
def players_list(request):
    if not check_access(request):
        return JsonResponse({"error": "Доступ запрещён: требуется вход или API ключ"}, status=403)

    players = Player.objects.all().values(
        "id", "first_name", "last_name", "age", "level", "address", "phone_number"
    )
    return JsonResponse(list(players), safe=False)


def player_detail(request, id):
    if not check_access(request):
        return JsonResponse({"error": "Доступ запрещён: требуется вход или API ключ"}, status=403)

    try:
        player = Player.objects.values(
            "id", "first_name", "last_name", "age", "level", "address", "phone_number"
        ).get(pk=id)
    except Player.DoesNotExist:
        raise Http404("Игрок не найден")
    return JsonResponse(player, safe=False)


# ===== Матчи =====
def matches_list(request):
    if not check_access(request):
        return JsonResponse({"error": "Доступ запрещён: требуется вход или API ключ"}, status=403)

    matches = Match.objects.select_related("player1", "player2").all()
    data = []
    for m in matches:
        data.append({
            "id": m.id,
            "player1": str(m.player1),
            "player2": str(m.player2) if m.player2 else None,
            "date": m.date,
            "time": m.time,
            "location": m.location,
            "status": m.get_status_display(),
            "score": m.score,
        })
    return JsonResponse(data, safe=False)


def match_detail(request, id):
    if not check_access(request):
        return JsonResponse({"error": "Доступ запрещён: требуется вход или API ключ"}, status=403)

    try:
        m = Match.objects.select_related("player1", "player2").get(pk=id)
    except Match.DoesNotExist:
        raise Http404("Матч не найден")

    data = {
        "id": m.id,
        "player1": str(m.player1),
        "player2": str(m.player2) if m.player2 else None,
        "date": m.date,
        "time": m.time,
        "location": m.location,
        "status": m.get_status_display(),
        "score": m.score,
    }
    return JsonResponse(data, safe=False)


# ===== Турниры =====
def tournaments_list(request):
    if not check_access(request):
        return JsonResponse({"error": "Доступ запрещён: требуется вход или API ключ"}, status=403)

    tournaments = Tournament.objects.all().values("id", "name", "start_date", "end_date")
    return JsonResponse(list(tournaments), safe=False)


def tournament_detail(request, id):
    if not check_access(request):
        return JsonResponse({"error": "Доступ запрещён: требуется вход или API ключ"}, status=403)

    try:
        t = Tournament.objects.values("id", "name", "start_date", "end_date").get(pk=id)
    except Tournament.DoesNotExist:
        raise Http404("Турнир не найден")
    return JsonResponse(t, safe=False)
