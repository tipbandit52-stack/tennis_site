from django.db import models
from players.models import Player


class Match(models.Model):
    player1 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="matches_as_player1"
    )
    player2 = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        related_name="matches_as_player2",
        null=True,
        blank=True
    )
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)

    STATUS_CHOICES = [
        ("open", "Открыт (ищет соперника)"),
        ("scheduled", "Запланирован"),
        ("finished", "Завершён"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open"
    )

    score = models.CharField(
        max_length=50,
        blank=True,
        help_text="Например: 6-4, 3-6, 7-5"
    )

    def __str__(self):
        if self.player2:
            return f"{self.player1} vs {self.player2} — {self.date}"
        return f"{self.player1} vs (ожидает соперника) — {self.date}"

    def is_open(self):
        return self.player2 is None

    def players(self):
        return [self.player1] + ([self.player2] if self.player2 else [])
