# tennis_site/players/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
import base64, uuid, re, io
from PIL import Image

from .models import Player, Achievement
from .forms import PlayerForm, AchievementForm, PlayerProfileForm, PlayerFilterForm


# ================================================================
# 🔧 Декодирование base64 в Cloudinary-совместимый файл
# ================================================================
def _decode_base64_image(data_url: str):
    """
    Принимает строку вида 'data:image/jpeg;base64,...'
    Возвращает InMemoryUploadedFile для загрузки в Cloudinary.
    """
    if not data_url or not data_url.startswith("data:image"):
        return None

    try:
        match = re.match(r"^data:(image\/[a-zA-Z0-9.+-]+);base64,(.*)$", data_url)
        if not match:
            return None

        mime, b64data = match.groups()
        ext = {
            "image/jpeg": "jpg",
            "image/jpg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
        }.get(mime, "jpg")

        raw = base64.b64decode(b64data)
        unique_name = f"cropped_{uuid.uuid4().hex}.{ext}"

        # ✅ Создаём in-memory файл (чтобы Cloudinary мог принять)
        img = Image.open(io.BytesIO(raw))
        buffer = io.BytesIO()
        img.save(buffer, format=img.format or "JPEG")
        buffer.seek(0)

        return InMemoryUploadedFile(
            buffer, None, unique_name, mime, buffer.getbuffer().nbytes, None
        )

    except Exception as e:
        print(f"⚠️ Ошибка декодирования base64: {e}")
        return None


# ================================================================
# Главная страница
# ================================================================
def index(request):
    return render(request, "index.html")


# ================================================================
# Список игроков
# ================================================================
class PlayerListView(ListView):
    model = Player
    template_name = "players/players_list.html"
    context_object_name = "players"

    def get_queryset(self):
        queryset = Player.objects.all()
        form = PlayerFilterForm(self.request.GET or None)

        if form.is_valid():
            name = form.cleaned_data.get("name")
            min_age = form.cleaned_data.get("min_age")
            max_age = form.cleaned_data.get("max_age")
            level = form.cleaned_data.get("level")
            address = form.cleaned_data.get("address")

            if name:
                queryset = queryset.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name))
            if min_age:
                queryset = queryset.filter(age__gte=min_age)
            if max_age:
                queryset = queryset.filter(age__lte=max_age)
            if level:
                queryset = queryset.filter(level=level)
            if address:
                queryset = queryset.filter(address__icontains=address)

        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form"] = PlayerFilterForm(self.request.GET or None)
        return ctx


# ================================================================
# Создание профиля игрока
# ================================================================
@login_required
def create_player_profile(request):
    if hasattr(request.user, "player_profile") and request.user.player_profile:
        return redirect("player_profile_edit")

    if request.method == "POST":
        form = PlayerProfileForm(request.POST, request.FILES)
        if form.is_valid():
            player = form.save(commit=False)
            player.user = request.user

            photo_data = request.POST.get("photo_data")
            cropped = _decode_base64_image(photo_data)
            if cropped:
                player.photo = cropped

            try:
                player.save()
                messages.success(request, "Профиль успешно создан!")
                return redirect("my_profile")
            except Exception as e:
                print("⚠️ Ошибка сохранения профиля:", e)
                messages.error(request, "Ошибка при сохранении профиля.")
    else:
        initial = {}
        if request.user.first_name:
            initial["first_name"] = request.user.first_name
        if request.user.last_name:
            initial["last_name"] = request.user.last_name
        form = PlayerProfileForm(initial=initial)

    return render(request, "players/player_profile_form.html", {"form": form, "edit_mode": False})


# ================================================================
# Редактирование профиля игрока
# ================================================================
@login_required
def edit_my_player_profile(request):
    player = getattr(request.user, "player_profile", None)
    if not player:
        return redirect("player_create_profile")

    if request.method == "POST":
        form = PlayerProfileForm(request.POST, request.FILES, instance=player)
        if form.is_valid():
            player = form.save(commit=False)

            photo_data = request.POST.get("photo_data")
            cropped = _decode_base64_image(photo_data)
            if cropped:
                player.photo = cropped

            try:
                player.save()
                messages.success(request, "Профиль обновлён!")
                return redirect("my_profile")
            except Exception as e:
                print("⚠️ Ошибка сохранения профиля:", e)
                messages.error(request, "Не удалось сохранить изменения.")
    else:
        form = PlayerProfileForm(instance=player)

    return render(request, "players/player_profile_form.html", {"form": form, "edit_mode": True})


# ================================================================
# Просмотр собственного профиля
# ================================================================
@login_required
def my_profile(request):
    player = getattr(request.user, "player_profile", None)
    if not player:
        return redirect("player_create_profile")
    return redirect("player_detail", pk=player.pk)


# ================================================================
# Деталка игрока
# ================================================================
class PlayerDetailView(DetailView):
    model = Player
    template_name = "players/player_detail.html"
    context_object_name = "player"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["achievements"] = self.object.achievements.all().order_by("-date")
        my_user = self.request.user
        if my_user.is_authenticated:
            from friends.models import Friendship
            ctx["friendships"] = Friendship.objects.filter(
                Q(from_player=my_user, to_player=self.object.user)
                | Q(from_player=self.object.user, to_player=my_user)
            )
        else:
            ctx["friendships"] = None

        my_profile = getattr(my_user, "player_profile", None)
        ctx["can_invite_to_match"] = (my_profile is not None and my_profile != self.object)
        return ctx


# ================================================================
# CRUD Player
# ================================================================
class PlayerCreateView(CreateView):
    model = Player
    form_class = PlayerForm
    template_name = "players/player_form.html"
    success_url = reverse_lazy("players_list")


class PlayerUpdateView(UpdateView):
    model = Player
    form_class = PlayerForm
    template_name = "players/player_form.html"
    success_url = reverse_lazy("players_list")


class PlayerDeleteView(DeleteView):
    model = Player
    template_name = "players/player_confirm_delete.html"
    success_url = reverse_lazy("players_list")


# ================================================================
# Достижения
# ================================================================
@login_required
def add_achievement(request, pk):
    player = get_object_or_404(Player, pk=pk)
    if request.user != player.user:
        messages.error(request, "Вы не можете добавлять достижения другому игроку.")
        return redirect("player_detail", pk=pk)

    if request.method == "POST":
        form = AchievementForm(request.POST, request.FILES)
        if form.is_valid():
            ach = form.save(commit=False)
            ach.player = player

            photo_data = request.POST.get("photo_data")
            cropped = _decode_base64_image(photo_data)
            if cropped:
                ach.photo = cropped

            try:
                ach.save()
                messages.success(request, "Достижение добавлено!")
                return redirect("player_detail", pk=pk)
            except Exception as e:
                print("⚠️ Ошибка сохранения достижения:", e)
                messages.error(request, "Ошибка при добавлении достижения.")
    else:
        form = AchievementForm()

    return render(request, "achievements/achievement_form.html", {"form": form, "player": player})


@login_required
def edit_achievement(request, pk):
    achievement = get_object_or_404(Achievement, pk=pk, player=request.user.player_profile)

    if request.method == "POST":
        form = AchievementForm(request.POST, request.FILES, instance=achievement)
        if form.is_valid():
            ach = form.save(commit=False)

            photo_data = request.POST.get("photo_data")
            cropped = _decode_base64_image(photo_data)
            if cropped:
                ach.photo = cropped

            try:
                ach.save()
                messages.success(request, "Изменения сохранены!")
                return redirect("player_detail", pk=achievement.player.pk)
            except Exception as e:
                print("⚠️ Ошибка сохранения достижения:", e)
                messages.error(request, "Ошибка при сохранении достижения.")
    else:
        form = AchievementForm(instance=achievement)

    return render(request, "achievements/achievement_form.html", {
        "form": form,
        "edit_mode": True,
        "player": achievement.player,
    })


@login_required
def delete_achievement(request, pk):
    achievement = get_object_or_404(Achievement, pk=pk, player=request.user.player_profile)

    if request.method == "POST":
        achievement.delete()
        messages.success(request, "Достижение удалено!")
        return redirect("player_detail", pk=achievement.player.pk)

    return render(request, "achievements/achievement_confirm_delete.html", {"achievement": achievement})
