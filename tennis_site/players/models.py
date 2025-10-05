from django.db import models
from django.contrib.auth.models import User
import uuid, os

LEVEL_CHOICES = [(str(x), f"NTRP {x:.1f}") for x in [i * 0.5 for i in range(2, 15)]]

def player_photo_upload(instance, filename):
    ext = os.path.splitext(filename)[1] or ".jpg"
    return f"players_photos/{uuid.uuid4().hex}{ext}"

def achievement_photo_upload(instance, filename):
    ext = os.path.splitext(filename)[1] or ".jpg"
    return f"achievements_photos/{uuid.uuid4().hex}{ext}"

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="player_profile", blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField()
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES)
    photo = models.ImageField(upload_to=player_photo_upload, blank=True, null=True)
    phone_number = models.CharField("Телефон", max_length=20, blank=True, null=True)
    address = models.CharField("Адрес проживания", max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Игрок"
        verbose_name_plural = "Игроки"


class Achievement(models.Model):
    player = models.ForeignKey("Player", on_delete=models.CASCADE, related_name="achievements")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date = models.DateField(auto_now_add=True)
    photo = models.ImageField(upload_to=achievement_photo_upload, blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.player.first_name})"

    class Meta:
        verbose_name = "Достижение"
        verbose_name_plural = "Достижения"
