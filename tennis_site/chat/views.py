from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Max
from django.utils.dateparse import parse_datetime
from django.contrib import messages

from .models import Chat, Message
from players.models import Player


# ------------------- Вспомогательные -------------------

def _abs_photo_url(request, player: Player):
    """Вернуть абсолютный URL фото игрока (если есть)."""
    if getattr(player, "photo", None) and player.photo:
        try:
            return request.build_absolute_uri(player.photo.url)
        except Exception:
            return None
    return None


def _ensure_participant_or_403(request, chat: Chat):
    """Проверить, что текущий пользователь — участник чата."""
    me = request.user.player_profile
    if not chat.participants.filter(id=me.id).exists():
        return HttpResponseForbidden("Not a chat participant")
    return None


# ------------------- Представления -------------------

@login_required
def inbox(request):
    """Список чатов текущего пользователя."""
    me = request.user.player_profile
    chats = (
        Chat.objects.filter(participants=me)
        .prefetch_related("participants")
        .annotate(last_at=Max("messages__created_at"))
        .order_by("-last_at", "-id")
    )

    data = []
    for ch in chats:
        other = ch.other_for(me)
        last = ch.last_message()
        unread = ch.messages.filter(is_read=False).exclude(sender=me).count()
        data.append({
            "chat": ch,
            "other": other,
            "other_photo": _abs_photo_url(request, other) if other else None,
            "last_message": last,
            "unread": unread,
        })

    return render(request, "chat/inbox.html", {"items": data})


@login_required
def chat_with(request, player_id):
    """Открыть или создать чат с игроком."""
    me = request.user.player_profile
    other = get_object_or_404(Player, pk=player_id)

    chat = (
        Chat.objects.filter(participants=me)
        .filter(participants=other)
        .first()
    )
    if not chat:
        chat = Chat.objects.create()
        chat.participants.add(me, other)

    chat_messages = chat.messages.select_related("sender").order_by("created_at")

    # все входящие помечаем прочитанными
    chat.messages.filter(is_read=False).exclude(sender=me).update(is_read=True)

    return render(
        request,
        "chat/chat_detail.html",
        {
            "chat": chat,
            "chat_messages": chat_messages,
            "other": other,
            "other_photo": _abs_photo_url(request, other),
        },
    )


@login_required
def delete_chat(request, chat_id):
    """Удалить чат целиком."""
    chat = get_object_or_404(Chat, id=chat_id)
    forbid = _ensure_participant_or_403(request, chat)
    if forbid:
        return forbid

    if request.method == "POST":
        chat.delete()
        messages.success(request, "Чат успешно удалён.")
        return redirect("chat:inbox")

    other = chat.other_for(request.user.player_profile)
    return render(request, "chat/chat_confirm_delete.html", {"chat": chat, "other": other})


# ------------------- API -------------------

@login_required
def api_send(request, chat_id):
    """POST: отправить сообщение в чат."""
    if request.method != "POST":
        return JsonResponse({"error": "bad request"}, status=400)

    chat = get_object_or_404(Chat, id=chat_id)
    forbid = _ensure_participant_or_403(request, chat)
    if forbid:
        return forbid

    import json
    payload = json.loads(request.body or "{}")
    text = (payload.get("text") or "").strip()
    if not text:
        return JsonResponse({"error": "empty"}, status=400)

    me = request.user.player_profile
    msg = Message.objects.create(chat=chat, sender=me, text=text)

    return JsonResponse(
        {
            "message": {
                "id": msg.id,
                "text": msg.text,
                "sender_name": msg.sender.first_name,
                "sender_photo": _abs_photo_url(request, msg.sender),
                "mine": True,
                "created_at": msg.created_at.isoformat(),
            }
        },
        status=201,
    )


@login_required
def api_messages(request, chat_id):
    """GET: получить сообщения (с фильтром по after)."""
    chat = get_object_or_404(Chat, id=chat_id)
    forbid = _ensure_participant_or_403(request, chat)
    if forbid:
        return forbid

    after = request.GET.get("after")
    qs = chat.messages.select_related("sender").order_by("created_at")
    if after:
        after_dt = parse_datetime(after)
        if after_dt:
            qs = qs.filter(created_at__gt=after_dt)

    me = request.user.player_profile
    msgs = [
        {
            "id": m.id,
            "text": m.text,
            "sender_name": m.sender.first_name,
            "sender_photo": _abs_photo_url(request, m.sender),
            "mine": (m.sender_id == me.id),
            "created_at": m.created_at.isoformat(),
        }
        for m in qs
    ]

    chat.messages.filter(is_read=False).exclude(sender=me).update(is_read=True)

    return JsonResponse({"messages": msgs})


@login_required
def api_mark_read(request, chat_id):
    """POST: пометить входящие как прочитанные."""
    if request.method != "POST":
        return JsonResponse({"error": "bad request"}, status=400)

    chat = get_object_or_404(Chat, id=chat_id)
    forbid = _ensure_participant_or_403(request, chat)
    if forbid:
        return forbid

    me = request.user.player_profile
    chat.messages.filter(is_read=False).exclude(sender=me).update(is_read=True)
    return JsonResponse({"ok": True})


@login_required
def api_unread_count(request):
    """Общий счётчик непрочитанных сообщений."""
    me = request.user.player_profile
    count = (
        Message.objects
        .filter(chat__participants=me, is_read=False)
        .exclude(sender=me)
        .count()
    )
    return JsonResponse({"count": count})


@login_required
def api_unread_per_chat(request):
    """Счётчик непрочитанных по каждому чату."""
    me = request.user.player_profile
    chats = Chat.objects.filter(participants=me).distinct().prefetch_related("participants")

    data = []
    for chat in chats:
        other = chat.other_for(me)
        unread = chat.messages.filter(is_read=False).exclude(sender=me).count()
        data.append({
            "chat_id": chat.id,
            "other_name": f"{other.first_name} {other.last_name}" if other else "Без имени",
            "other_photo": _abs_photo_url(request, other) if other else None,
            "unread": unread,
        })

    return JsonResponse({"chats": data})
