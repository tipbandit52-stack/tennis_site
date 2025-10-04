from django.db import models
from django.contrib.auth.models import User

LEVEL_CHOICES = [(str(x), f"NTRP {x:.1f}") for x in [i * 0.5 for i in range(2, 15)]]  # 1.0..7.0

class Player(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="player_profile",
        blank=True, null=True
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField()
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES)
    photo = models.ImageField(upload_to='players_photos/', blank=True, null=True)

    phone_number = models.CharField("Телефон", max_length=20, blank=True, null=True)
    address = models.CharField("Адрес проживания", max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Achievement(models.Model):
    player = models.ForeignKey("Player", on_delete=models.CASCADE, related_name="achievements")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date = models.DateField(auto_now_add=True)
    photo = models.ImageField(upload_to='achievements_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.player.first_name} {self.player.last_name}"
