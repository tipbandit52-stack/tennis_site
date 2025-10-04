from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Friendship


@login_required
def friends_list(request):
    user = request.user

    # Какая вкладка активна (friends | incoming | outgoing)
    active_tab = request.GET.get("tab", "friends")
    if active_tab not in ("friends", "incoming", "outgoing"):
        active_tab = "friends"

    # Подтверждённые дружбы
    friendships = Friendship.objects.filter(
        Q(from_player=user, is_accepted=True) | Q(to_player=user, is_accepted=True)
    )

    friends = []
    for fr in friendships:
        other_user = fr.to_player if fr.from_player == user else fr.from_player
        profile = getattr(other_user, "player_profile", None)
        if profile:
            friends.append({"player": profile, "friendship_pk": fr.pk})

    # Входящие заявки
    incoming = []
    for fr in Friendship.objects.filter(to_player=user, is_accepted=False):
        profile = getattr(fr.from_player, "player_profile", None)
        if profile:
            incoming.append({"player": profile, "friendship_pk": fr.pk})

    # Исходящие заявки
    outgoing = []
    for fr in Friendship.objects.filter(from_player=user, is_accepted=False):
        profile = getattr(fr.to_player, "player_profile", None)
        if profile:
            outgoing.append({"player": profile, "friendship_pk": fr.pk})

    return render(
        request,
        "friends/friends_list.html",
        {
            "friends": friends,
            "incoming_requests": incoming,
            "outgoing_requests": outgoing,
            "active_tab": active_tab,
        },
    )


@login_required
@require_POST
def send_friend_request(request, user_id):
    """Отправка заявки из профиля игрока."""
    other = get_object_or_404(User, pk=user_id)
    if other == request.user:
        messages.error(request, "Нельзя отправить заявку самому себе.")
        return redirect("friends_list")

    exists = Friendship.objects.filter(
        Q(from_player=request.user, to_player=other) |
        Q(from_player=other, to_player=request.user)
    ).exists()

    if exists:
        messages.info(request, "Заявка уже существует или вы уже друзья.")
    else:
        Friendship.objects.create(from_player=request.user, to_player=other)
        messages.success(request, f"Заявка пользователю {other.username} отправлена.")

    prof = getattr(other, "player_profile", None)
    if prof:
        return redirect("player_detail", pk=prof.pk)
    return redirect("friends_list")


def _redirect_with_tab(request, default_tab="friends"):
    """Возвращает redirect на список друзей c сохранением вкладки."""
    tab = request.GET.get("tab", default_tab)
    if tab not in ("friends", "incoming", "outgoing"):
        tab = default_tab
    return redirect(f"{reverse('friends_list')}?tab={tab}")


@login_required
def accept_friend(request, pk):
    friendship = get_object_or_404(Friendship, pk=pk, to_player=request.user, is_accepted=False)
    friendship.is_accepted = True
    friendship.save(update_fields=["is_accepted"])
    messages.success(request, f"Вы приняли заявку от {friendship.from_player.username}.")
    return _redirect_with_tab(request, default_tab="incoming")


@login_required
def reject_friend(request, pk):
    friendship = get_object_or_404(Friendship, pk=pk, to_player=request.user, is_accepted=False)
    messages.info(request, f"Вы отклонили заявку от {friendship.from_player.username}.")
    friendship.delete()
    return _redirect_with_tab(request, default_tab="incoming")


@login_required
def cancel_request(request, pk):
    friendship = get_object_or_404(Friendship, pk=pk, from_player=request.user, is_accepted=False)
    messages.info(request, f"Вы отменили заявку пользователю {friendship.to_player.username}.")
    friendship.delete()
    return _redirect_with_tab(request, default_tab="outgoing")


@login_required
def remove_friend(request, pk):
    friendship = get_object_or_404(Friendship, pk=pk, is_accepted=True)
    if friendship.from_player == request.user or friendship.to_player == request.user:
        friendship.delete()
        messages.success(request, "Друг удалён.")
    else:
        messages.error(request, "Вы не можете удалить эту дружбу.")
    return _redirect_with_tab(request, default_tab="friends")
