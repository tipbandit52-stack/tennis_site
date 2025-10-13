from django.db import models
from django.contrib.auth.models import User
import uuid, os


# === 1. Уровни NTRP (1.0–7.0) ===
LEVEL_CHOICES = [
    (str(x), f"NTRP {x:.1f}") for x in [i * 0.5 for i in range(2, 15)]
]


# === 2. Уникальные пути сохранения ===
def player_photo_upload(instance, filename):
    """
    Сохраняет фото игроков в media/players_photos/
    с уникальным именем (UUID), чтобы избежать конфликтов.
    """
    ext = os.path.splitext(filename)[1].lower() or ".jpg"
    return f"players_photos/{uuid.uuid4().hex}{ext}"


def achievement_photo_upload(instance, filename):
    """
    Сохраняет фото достижений в media/achievements_photos/
    """
    ext = os.path.splitext(filename)[1].lower() or ".jpg"
    return f"achievements_photos/{uuid.uuid4().hex}{ext}"


# === 3. Модель Игрока ===
class Player(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="player_profile",
        blank=True,
        null=True,
    )
    first_name = models.CharField("Имя", max_length=50)
    last_name = models.CharField("Фамилия", max_length=50)
    age = models.PositiveIntegerField("Возраст")
    level = models.CharField("Уровень NTRP", max_length=50, choices=LEVEL_CHOICES)

    # Фото игрока
    photo = models.ImageField(
        "Фото игрока",
        upload_to=player_photo_upload,
        blank=True,
        null=True,
    )

    phone_number = models.CharField("Телефон", max_length=20, blank=True, null=True)
    address = models.CharField("Адрес проживания", max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Игрок"
        verbose_name_plural = "Игроки"
        ordering = ["last_name", "first_name"]


# === 4. Модель Достижения ===
class Achievement(models.Model):
    player = models.ForeignKey(
        "Player",
        on_delete=models.CASCADE,
        related_name="achievements",
        verbose_name="Игрок",
    )
    title = models.CharField("Название", max_length=100)
    description = models.TextField("Описание", blank=True)
    date = models.DateField("Дата добавления", auto_now_add=True)

    photo = models.ImageField(
        "Фото достижения",
        upload_to=achievement_photo_upload,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.title} — {self.player.first_name} {self.player.last_name}"

    class Meta:
        verbose_name = "Достижение"
        verbose_name_plural = "Достижения"
        ordering = ["-date"]
