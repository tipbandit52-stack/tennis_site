import math
import random
from functools import reduce
from operator import or_ as OR
from decimal import Decimal, InvalidOperation
from typing import List, Optional, Dict

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q

from .models import Tournament, Group, GroupMatch, BracketMatch
from .forms import TournamentForm
from players.models import Player

# Константы для фильтра/форм
LEVEL_OPTIONS = ["1.0","1.5","2.0","2.5","3.0","3.5","4.0","4.5","5.0","5.5","6.0","6.5","7.0"]
FORMAT_OPTIONS = [16, 32, 64]


# ========== Вспомогательные ==========
def _to_decimal(value):
    """Безопасно привести значение к Decimal (поддерживает '5,5')."""
    if value is None or value == "":
        return None
    if isinstance(value, Decimal):
        return value
    s = str(value).strip().replace(",", ".")
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None


def _next_pow2(n: int) -> int:
    """Следующая степень двойки >= n."""
    if n <= 1:
        return 1
    return 1 << (n - 1).bit_length()


def _pairs_round_robin(players: List[Player]) -> List[tuple]:
    """Пары для кругового турнира в группе."""
    pairs = []
    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            pairs.append((players[i], players[j]))
    return pairs


def _calc_group_table(group: Group) -> List[Dict]:
    """Подсчёт таблицы группы."""
    players_set = set()
    for gm in group.matches.select_related("p1", "p2").all():
        if gm.p1:
            players_set.add(gm.p1)
        if gm.p2:
            players_set.add(gm.p2)

    table = {p.pk: {"player": p, "w": 0, "l": 0, "pf": 0, "pa": 0, "pts": 0} for p in players_set}

    for gm in group.matches.all():
        if gm.p1 and gm.p2 and gm.p1_score is not None and gm.p2_score is not None:
            p1id, p2id = gm.p1.pk, gm.p2.pk
            table[p1id]["pf"] += gm.p1_score
            table[p1id]["pa"] += gm.p2_score
            table[p2id]["pf"] += gm.p2_score
            table[p2id]["pa"] += gm.p1_score

            if gm.p1_score > gm.p2_score:
                table[p1id]["w"] += 1
                table[p2id]["l"] += 1
                table[p1id]["pts"] += 2
            elif gm.p2_score > gm.p1_score:
                table[p2id]["w"] += 1
                table[p1id]["l"] += 1
                table[p2id]["pts"] += 2
            else:
                table[p1id]["pts"] += 1
                table[p2id]["pts"] += 1

    rows = []
    for row in table.values():
        row["diff"] = row["pf"] - row["pa"]
        rows.append(row)

    rows.sort(key=lambda r: (r["pts"], r["diff"], r["pf"]), reverse=True)
    return rows


def _create_groups_for_tournament(tour: Tournament, group_size: int = 4):
    """
    Пересоздать группы: удалить старые, рандомно распределить игроков,
    создать все матчи внутри групп.
    """
    tour.groups.all().delete()

    players = list(tour.players.all())
    if len(players) < 2:
        tour.status = "GRP"
        tour.save()
        return

    random.shuffle(players)

    def code(i: int) -> str:
        return chr(ord("A") + i)

    chunks = [players[i:i + group_size] for i in range(0, len(players), group_size)]
    for idx, chunk in enumerate(chunks):
        g = Group.objects.create(tournament=tour, code=code(idx))
        for p1, p2 in _pairs_round_robin(chunk):
            GroupMatch.objects.create(group=g, p1=p1, p2=p2)

    tour.status = "GRP"
    tour.save()


def _create_bracket_for_tournament(tour: Tournament, seed_from: Optional[List[Player]] = None):
    """
    Пересоздать плей-офф: удалить старую сетку, создать 1-й раунд и пустые матчи
    последующих раундов.
    """
    tour.bracket_matches.all().delete()

    players = seed_from[:] if seed_from else list(tour.players.all())

    # 0 или 1 участник — матчей нет
    if len(players) <= 1:
        tour.status = "KO"
        tour.save()
        return

    size = _next_pow2(len(players))
    while len(players) < size:
        players.append(None)

    random.shuffle(players)
    total_rounds = int(math.log2(size))

    # Раунд 1
    slot = 1
    for i in range(0, size, 2):
        BracketMatch.objects.create(
            tournament=tour,
            round_no=1,
            slot=slot,
            p1=players[i],
            p2=players[i + 1],
        )
        slot += 1

    # Остальные раунды (пустые матчи)
    prev = size // 2
    for r in range(2, total_rounds + 1):
        for s in range(1, prev // 2 + 1):
            BracketMatch.objects.create(
                tournament=tour,
                round_no=r,
                slot=s,
                p1=None,
                p2=None,
            )
        prev //= 2

    tour.status = "KO"
    tour.save()


# ========== Список турниров + фильтры ==========
@login_required
def tournaments_list(request):
    qs = Tournament.objects.all().order_by("date")

    q = request.GET.get("q", "").strip()
    city = request.GET.get("city", "").strip()

    # форматы: fmt=16&fmt=32...
    formats_selected = request.GET.getlist("fmt")

    # уровни: поддержим и старое имя 'lvl', и новое 'levels'
    levels_selected = request.GET.getlist("levels") or request.GET.getlist("lvl")

    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(location__icontains=q))
    if city:
        qs = qs.filter(location__icontains=city)

    if formats_selected:
        try:
            fmt_ints = [int(x) for x in formats_selected]
            qs = qs.filter(format__in=fmt_ints)
        except ValueError:
            pass

    if levels_selected:
        parts = []
        for s in levels_selected:
            try:
                lvl = Decimal(s.replace(",", "."))
            except Exception:
                continue
            parts.append(
                (Q(min_level__isnull=True) | Q(min_level__lte=lvl)) &
                (Q(max_level__isnull=True) | Q(max_level__gte=lvl))
            )
        if parts:
            qs = qs.filter(reduce(OR, parts))

    ctx = {
        "tournaments": qs,
        "q": q,
        "city": city,
        "formats_selected": [str(x) for x in formats_selected],
        "levels_selected": levels_selected,
        "FORMAT_OPTIONS": FORMAT_OPTIONS,
        "LEVEL_OPTIONS": LEVEL_OPTIONS,
        # показывать панель по умолчанию; принимаем 1/open/true/yes
        "show_filters": (request.GET.get("filters", "1").lower() in {"1", "open", "true", "yes"}),
    }
    return render(request, "tournaments/tournaments_list.html", ctx)


# ========== Детали турнира ==========
class TournamentDetailView(DetailView):
    model = Tournament
    template_name = "tournaments/tournament_detail.html"
    context_object_name = "tournament"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tour: Tournament = self.object

        ctx["participants"] = tour.players.all()
        ctx["groups"] = tour.groups.all().order_by("code")

        rounds = {}
        for m in tour.bracket_matches.select_related("p1", "p2"):
            rounds.setdefault(m.round_no, []).append(m)
        for r in rounds:
            rounds[r] = sorted(rounds[r], key=lambda x: x.slot)
        ctx["rounds"] = rounds

        user = self.request.user
        ctx["can_manage"] = user.is_authenticated and (user == tour.creator or user.is_superuser)
        return ctx


# ========== CRUD ==========
class TournamentCreateView(LoginRequiredMixin, CreateView):
    model = Tournament
    form_class = TournamentForm
    template_name = "tournaments/tournament_form.html"
    success_url = reverse_lazy("tournaments:tournaments_list")
    login_url = "login"

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


class TournamentUpdateView(LoginRequiredMixin, UpdateView):
    model = Tournament
    form_class = TournamentForm
    template_name = "tournaments/tournament_form.html"
    success_url = reverse_lazy("tournaments:tournaments_list")
    login_url = "login"


class TournamentDeleteView(LoginRequiredMixin, DeleteView):
    model = Tournament
    template_name = "tournaments/tournament_confirm_delete.html"
    success_url = reverse_lazy("tournaments:tournaments_list")
    login_url = "login"


# ========== Участие ==========
@login_required
def tournament_join(request, pk):
    tour = get_object_or_404(Tournament, pk=pk)
    me = getattr(request.user, "player_profile", None)

    if not me:
        messages.error(request, "У вас нет профиля игрока.")
        return redirect("tournaments:tournament_detail", pk=pk)

    if tour.players.filter(pk=me.pk).exists():
        messages.info(request, "Вы уже участвуете в турнире.")
        return redirect("tournaments:tournament_detail", pk=pk)

    # лимит мест (если есть поле)
    if hasattr(tour, "max_players") and tour.max_players:
        if tour.players.count() >= tour.max_players:
            messages.error(request, "Турнир уже заполнен.")
            return redirect("tournaments:tournament_detail", pk=pk)

    # проверка уровня
    me_level = _to_decimal(getattr(me, "level", None))
    if (tour.min_level or tour.max_level) and me_level is None:
        messages.error(request, "Для участия укажите уровень в профиле игрока.")
        return redirect("tournaments:tournament_detail", pk=pk)

    if tour.min_level is not None and me_level is not None and me_level < tour.min_level:
        messages.error(request, f"Минимальный уровень турнира: {tour.min_level}. Ваш: {getattr(me, 'level', '—')}.")
        return redirect("tournaments:tournament_detail", pk=pk)

    if tour.max_level is not None and me_level is not None and me_level > tour.max_level:
        messages.error(request, f"Максимальный уровень турнира: {tour.max_level}. Ваш: {getattr(me, 'level', '—')}.")
        return redirect("tournaments:tournament_detail", pk=pk)

    tour.players.add(me)
    messages.success(request, "Вы присоединились к турниру!")
    return redirect("tournaments:tournament_detail", pk=pk)


@login_required
def tournament_leave(request, pk):
    tour = get_object_or_404(Tournament, pk=pk)
    me = getattr(request.user, "player_profile", None)
    if not me:
        messages.error(request, "Профиль игрока не найден.")
        return redirect("tournaments:tournament_detail", pk=pk)

    if tour.players.filter(pk=me.pk).exists():
        tour.players.remove(me)
        messages.success(request, "Вы покинули турнир.")
    else:
        messages.info(request, "Вы не были участником.")
    return redirect("tournaments:tournament_detail", pk=pk)


# ========== Генерация (только автор/админ) ==========
@login_required
@require_POST
def tournament_generate_groups_anytime(request, pk):
    tour = get_object_or_404(Tournament, pk=pk)
    if request.user != tour.creator and not request.user.is_superuser:
        messages.error(request, "Только автор или администратор может генерировать группы.")
        return redirect("tournaments:tournament_detail", pk=pk)

    try:
        group_size = int(request.POST.get("group_size", 4))
        group_size = max(2, min(group_size, 8))
    except ValueError:
        group_size = 4

    _create_groups_for_tournament(tour, group_size=group_size)
    messages.success(request, f"Группы созданы (по {group_size} игрока).")
    return redirect("tournaments:tournament_detail", pk=pk)


@login_required
@require_POST
def tournament_generate_knockout_any(request, pk):
    tour = get_object_or_404(Tournament, pk=pk)
    if request.user != tour.creator and not request.user.is_superuser:
        messages.error(request, "Только автор или администратор может генерировать плей-офф.")
        return redirect("tournaments:tournament_detail", pk=pk)

    _create_bracket_for_tournament(tour, seed_from=None)
    messages.success(request, "Сетка плей-офф создана.")
    return redirect("tournaments:tournament_detail", pk=pk)


# Алиасы (если где-то остались старые ссылки)
@login_required
@require_POST
def tournament_generate_bracket_anytime(request, pk):
    return tournament_generate_knockout_any(request, pk)


@login_required
@require_POST
def tournament_generate_groups_any(request, pk):
    return tournament_generate_groups_anytime(request, pk)


# ========== Группы/Плей-офф: ввод счёта ==========
@login_required
def group_detail(request, pk):
    g = get_object_or_404(Group, pk=pk)
    table = _calc_group_table(g)
    return render(request, "tournaments/group_detail.html", {"group": g, "table": table})


@login_required
@require_POST
def group_set_score(request, match_id):
    gm = get_object_or_404(GroupMatch, pk=match_id)
    tour = gm.group.tournament
    if request.user != tour.creator and not request.user.is_superuser:
        messages.error(request, "Счёт может менять только автор/администратор.")
        return redirect("tournaments:group_detail", pk=gm.group.pk)

    def to_int_or_none(v):
        return None if v in (None, "",) else int(v)

    try:
        gm.p1_score = to_int_or_none(request.POST.get("p1_score"))
        gm.p2_score = to_int_or_none(request.POST.get("p2_score"))
    except ValueError:
        messages.error(request, "Неверный формат счёта.")
        return redirect("tournaments:group_detail", pk=gm.group.pk)

    if gm.p1_score is not None and gm.p2_score is not None:
        gm.winner = gm.p1 if gm.p1_score > gm.p2_score else gm.p2
    else:
        gm.winner = None
    gm.save()
    messages.success(request, "Счёт сохранён.")
    return redirect("tournaments:group_detail", pk=gm.group.pk)


@login_required
@require_POST
def bracket_set_score(request, match_id):
    match = get_object_or_404(BracketMatch, pk=match_id)
    tour = match.tournament
    if request.user != tour.creator and not request.user.is_superuser:
        messages.error(request, "Счёт может менять только автор/администратор.")
        return redirect("tournaments:tournament_detail", pk=tour.pk)

    try:
        p1 = int(request.POST.get("p1_score", ""))
        p2 = int(request.POST.get("p2_score", ""))
    except ValueError:
        messages.error(request, "Неверный формат счёта.")
        return redirect("tournaments:tournament_detail", pk=tour.pk)

    match.p1_score = p1
    match.p2_score = p2
    match.winner = match.p1 if p1 > p2 else match.p2
    match.save()

    messages.success(request, "Счёт плей-офф сохранён.")
    return redirect("tournaments:tournament_detail", pk=tour.pk)
