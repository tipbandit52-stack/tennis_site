from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # сразу авторизуем
            messages.success(request, "✅ Аккаунт успешно создан!")
            return redirect("player_create_profile")  # сразу на создание профиля
        else:
            messages.error(request, "❌ Ошибка при регистрации. Проверьте данные.")
    else:
        form = UserCreationForm()

    return render(request, "users/register.html", {"form": form})
