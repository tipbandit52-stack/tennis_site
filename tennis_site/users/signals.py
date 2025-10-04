from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from players.models import Player

@receiver(post_save, sender=User)
def create_player_profile(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(
            user=instance,
            first_name=instance.first_name or instance.username,
            last_name=instance.last_name or "",
            age=0,
            level="1.0"
        )
