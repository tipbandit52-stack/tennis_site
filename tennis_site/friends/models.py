from django.db import models
from django.conf import settings

class Friendship(models.Model):
    from_player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="friend_requests_sent",
        on_delete=models.CASCADE
    )
    to_player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="friend_requests_received",
        on_delete=models.CASCADE
    )
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Принято" if self.is_accepted else "Ожидает"
        return f"{self.from_player} → {self.to_player} ({status})"
