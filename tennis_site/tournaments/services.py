# tennis_site/tournaments/services.py
import math
import random
from typing import List

from django.db import transaction

from players.models import Player
from .models import Tournament, Group, GroupMatch, BracketMatch


# ===== Вспомогательные =====

def _shuffle_players(players: List[Player]) -> List[Player]:
    lst = list(players)
    random.shuffle(lst)
    return lst

def _all_pairs(lst: List[Player]):
    # круговой турнир в группе: все с каждым
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            yield lst[i], lst[j]


# ===== Генерация ГРУПП (рандом) =====
@transaction.atomic
def generate_groups_random(tour: Tournament, group_size: int = 4):
    """
    Рандомно распределяет всех участников по группам, сразу создаёт матчи внутри групп.
    Размер группы по умолчанию 4 (оптимально). Если игроков мало, размер сам подберётся.
    """
    # очистка старого
    tour.groups.all().delete()
    # если есть матчи плей-офф — тоже удалим
    tour.bracket_matches.all().delete()

    players = list(tour.players.all())
    if not players:
        return

    # подбираем разумный размер группы
    if len(players) < 8:
        group_size = max(3, min(4, len(players)))  # 3–4
    else:
        group_size = 4

    shuffled = _shuffle_players(players)
    groups_count = math.ceil(len(shuffled) / group_size)

    # создаём группы A, B, C...
    groups = []
    for idx in range(groups_count):
        code = chr(ord('A') + idx)
        g = Group.objects.create(tournament=tour, code=code)
        groups.append(g)

    # раскладываем игроков по группам «змейкой»
    for i, p in enumerate(shuffled):
        groups[i % groups_count].players.add(p)

    # создаём матчи внутри группы
    for g in groups:
        glist = list(g.players.all())
        for p1, p2 in _all_pairs(glist):
            GroupMatch.objects.create(group=g, p1=p1, p2=p2)

    tour.status = "GRP"
    tour.save()


# ===== Генерация ПЛЕЙ-ОФФ (для любого числа участников) =====
@transaction.atomic
def generate_knockout_bracket_any(tour: Tournament):
    """
    Строит сетку на ближайшую степень двойки >= числу участников.
    Лишние слоты получают BYE (пустые места).
    """
    # очистка старого
    tour.bracket_matches.all().delete()
    tour.groups.all().delete()

    players = list(tour.players.all())
    n = len(players)
    if n < 2:
        tour.status = "KO"
        tour.save()
        return

    # ближайшая степень двойки
    size = 1
    while size < n:
        size <<= 1

    # посев: просто перемешаем
    seeds = _shuffle_players(players)
    # добавим «пустые» места, если нужно
    while len(seeds) < size:
        seeds.append(None)

    # создаём 1-й раунд
    round_no = 1
    matches = []
    slot = 1
    for i in range(0, size, 2):
        p1 = seeds[i]
        p2 = seeds[i + 1]
        m = BracketMatch.objects.create(
            tournament=tour, round_no=round_no, slot=slot, p1=p1, p2=p2
        )
        matches.append(m)
        slot += 1

    # создаём пустые матчи следующих раундов
    prev_round_count = len(matches)
    while prev_round_count > 1:
        round_no += 1
        curr_round_count = prev_round_count // 2
        for s in range(1, curr_round_count + 1):
            BracketMatch.objects.create(
                tournament=tour, round_no=round_no, slot=s
            )
        prev_round_count = curr_round_count

    tour.status = "KO"
    tour.save()


# ===== Работа со счётом плей-офф (оставим как было) =====
def clear_downstream_from(match: BracketMatch):
    """
    Удалить «потомков» выигрыша начиная с данного матча.
    (Если у тебя уже есть реализация — можно её оставить, это базовая.)
    """
    # базовая очистка результата текущего
    match.winner = None
    match.p1_score = None
    match.p2_score = None
    match.save()
    # дальше можно ничего не делать, если связи на следующий матч рассчитываются по факту записи счёта


def record_bracket_score(match: BracketMatch, p1_score: int, p2_score: int):
    match.p1_score = p1_score
    match.p2_score = p2_score
    if p1_score > p2_score:
        match.winner = match.p1
    elif p2_score > p1_score:
        match.winner = match.p2
    else:
        match.winner = None
    match.save()
    # при желании здесь можно прокинуть победителя в следующий матч (если у тебя есть логика назначения p1/p2 следующего)


# ===== Подсчёт таблицы группы =====
def calc_group_table(group: Group):
    """
    Возвращает список словарей с полями:
    player, w (победы), l (поражения), pf (очки за), pa (очки против)
    Отсортировано по: победы desc, разница (pf-pa) desc, pf desc, имя.
    """
    rows = []
    stats = {}

    for pl in group.players.all():
        stats[pl.pk] = {"player": pl, "w": 0, "l": 0, "pf": 0, "pa": 0}

    for gm in group.matches.all() if hasattr(group, "matches") else GroupMatch.objects.filter(group=group):
        if gm.p1 and gm.p2 and gm.p1_score is not None and gm.p2_score is not None:
            stats[gm.p1.pk]["pf"] += gm.p1_score
            stats[gm.p1.pk]["pa"] += gm.p2_score
            stats[gm.p2.pk]["pf"] += gm.p2_score
            stats[gm.p2.pk]["pa"] += gm.p1_score
            if gm.p1_score > gm.p2_score:
                stats[gm.p1.pk]["w"] += 1
                stats[gm.p2.pk]["l"] += 1
            elif gm.p2_score > gm.p1_score:
                stats[gm.p2.pk]["w"] += 1
                stats[gm.p1.pk]["l"] += 1

    rows = list(stats.values())
    rows.sort(key=lambda r: (r["w"], r["pf"] - r["pa"], r["pf"], str(r["player"])), reverse=True)
    return rows


# ===== Посев из групп в плей-офф =====
def take_top_and_seed_knockout(tour: Tournament, take_from_group: int = 2):
    """
    Берёт топ-N из каждой группы, кидает в сетку плей-офф (any).
    """
    top_players = []
    for g in tour.groups.all().order_by("code"):
        table = calc_group_table(g)
        for idx, row in enumerate(table):
            if idx < take_from_group:
                top_players.append(row["player"])

    # перезаписываем участников турнира выбранными
    tour.players.set(top_players)
    generate_knockout_bracket_any(tour)
