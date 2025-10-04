import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

from .models import Chat, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room_group_name = f"chat_{self.chat_id}"

        user = self.scope.get("user")
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close()
            return

        # проверка: участник ли он чата
        is_participant = await self._is_participant(user.id, self.chat_id)
        if not is_participant:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data or "{}")
        message = (data.get("message") or "").strip()
        if not message:
            return

        user = self.scope["user"]
        saved_message = await self._save_message(user.id, self.chat_id, message)

        # шлём в комнату
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": saved_message["text"],
                "sender": saved_message["sender_name"],
                "sender_photo": saved_message["sender_photo"],
                "created_at": saved_message["created_at"],
                "mine_user_id": user.id,
            }
        )

        # нотификации (опционально — по группам пользователей)
        others = await self._other_user_ids(self.chat_id, user.id)
        for uid in others:
            await self.channel_layer.group_send(
                f"user_{uid}",
                {
                    "type": "notify",
                    "unread_count": await self._get_unread_count(uid),
                }
            )

    async def chat_message(self, event):
        # клиентский JS может сравнить user.id, если его туда передавать.
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "sender_photo": event["sender_photo"],
            "created_at": event["created_at"],
        }))

    @database_sync_to_async
    def _is_participant(self, user_id, chat_id):
        return Chat.objects.filter(id=chat_id, participants__user__id=user_id).exists()

    @database_sync_to_async
    def _save_message(self, user_id, chat_id, text):
        chat = Chat.objects.get(id=chat_id)
        sender = chat.participants.select_related("user").get(user__id=user_id)
        msg = Message.objects.create(chat=chat, sender=sender, text=text)
        photo = sender.photo.url if getattr(sender, "photo", None) and sender.photo else None
        return {
            "id": msg.id,
            "text": msg.text,
            "sender_name": sender.first_name,
            "sender_photo": photo,
            "created_at": msg.created_at.isoformat(),
        }

    @database_sync_to_async
    def _other_user_ids(self, chat_id, me_user_id):
        return list(
            Chat.objects.get(id=chat_id)
            .participants.exclude(user__id=me_user_id)
            .values_list("user__id", flat=True)
        )

    @database_sync_to_async
    def _get_unread_count(self, user_id):
        return (
            Message.objects
            .filter(chat__participants__user__id=user_id, is_read=False)
            .exclude(sender__user__id=user_id)
            .count()
        )


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user.is_authenticated:
            await self.close()
            return
        self.group_name = f"user_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify(self, event):
        await self.send(text_data=json.dumps({
            "unread_count": event["unread_count"]
        }))
