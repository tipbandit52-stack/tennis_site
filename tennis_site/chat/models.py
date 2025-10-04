from django.db import models
from django.utils import timezone
from players.models import Player


class Chat(models.Model):
    participants = models.ManyToManyField(Player, related_name="chats")

    def __str__(self):
        return f"Chat {self.pk}"

    def other_for(self, me: Player):
        """Вернёт второго участника чата относительно текущего игрока."""
        return self.participants.exclude(id=me.id).first()

    def last_message(self):
        return self.messages.order_by("-created_at").select_related("sender").first()


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(Player, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["chat", "created_at"]),
            models.Index(fields=["is_read"]),
        ]

    def __str__(self):
        return f"{self.sender} | {self.text[:30]}"
