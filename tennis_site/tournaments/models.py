from django.db import models
from django.conf import settings
from players.models import Player

class Tournament(models.Model):
    FORMAT_CHOICES = [
        (16, "16 игроков (плей-офф)"),
        (32, "32 игрока (плей-офф)"),
        (64, "64 игрока (группы + плей-офф)"),
    ]
    STATUS_CHOICES = [
        ("REG", "Регистрация"),
        ("GRP", "Группы"),
        ("KO", "Плей-офф"),
        ("DONE", "Завершён"),
    ]

    min_level = models.DecimalField(
        "Мин. уровень (NTRP)", max_digits=3, decimal_places=1, null=True, blank=True
    )
    max_level = models.DecimalField(
        "Макс. уровень (NTRP)", max_digits=3, decimal_places=1, null=True, blank=True
    )

    # полезно: возвращать читаемо
    def level_range_display(self):
        if self.min_level is None and self.max_level is None:
            return "любой"
        if self.min_level is None:
            return f"до {self.max_level}"
        if self.max_level is None:
            return f"от {self.min_level}"
        return f"{self.min_level} – {self.max_level}"

    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    format = models.PositiveIntegerField(choices=FORMAT_CHOICES, default=16)
    description = models.TextField(blank=True, null=True)

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_tournaments")
    status = models.CharField(max_length=4, choices=STATUS_CHOICES, default="REG")

    players = models.ManyToManyField(Player, blank=True, related_name="tournaments")

    @property
    def max_players(self):
        return self.format

    @property
    def is_open(self):
        return self.players.count() < self.max_players

    def __str__(self):
        return f"{self.name} ({self.location}, {self.date})"


class Group(models.Model):
    """Группа для формата 64 (16 групп по 4 игрока)."""
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="groups")
    code = models.CharField(max_length=2)  # 'A'..'P'
    players = models.ManyToManyField(Player, blank=True, related_name="groups")

    class Meta:
        unique_together = ("tournament", "code")

    def __str__(self):
        return f"{self.tournament.name} — группа {self.code}"


class GroupMatch(models.Model):
    """Матч в группе (каждый с каждым)."""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="matches")
    p1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="group_as_p1")
    p2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="group_as_p2")
    p1_score = models.PositiveIntegerField(null=True, blank=True)
    p2_score = models.PositiveIntegerField(null=True, blank=True)
    winner = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL, related_name="group_wins")

    class Meta:
        unique_together = ("group", "p1", "p2")

    def __str__(self):
        return f"[{self.group.code}] {self.p1} vs {self.p2}"


class BracketMatch(models.Model):
    """Узел плей-офф (дерево)."""
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="bracket_matches")
    round_no = models.PositiveIntegerField()  # 1 = первый раунд (1/16 для 32), 2 = 1/8, ... финал = log2(size)
    slot = models.PositiveIntegerField()      # номер пары внутри раунда, с 1

    p1 = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL, related_name="bracket_as_p1")
    p2 = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL, related_name="bracket_as_p2")

    p1_score = models.PositiveIntegerField(null=True, blank=True)
    p2_score = models.PositiveIntegerField(null=True, blank=True)
    winner = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL, related_name="bracket_wins")

    # связь вверх по дереву
    next_match = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="prev_matches")
    next_as_p1 = models.BooleanField(null=True, blank=True)  # True -> winner идёт в next.p1, False -> next.p2

    class Meta:
        unique_together = ("tournament", "round_no", "slot")
        ordering = ["round_no", "slot"]

    def __str__(self):
        return f"{self.tournament.name}: R{self.round_no} S{self.slot}"
