from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import modelform_factory
from django.db.models import Q
from .models import Match

# Если у тебя есть своя форма — импортируй. Иначе создаём на лету.
try:
    from .forms import MatchForm as _MatchForm
    MatchForm = _MatchForm
except Exception:
    # Важно: player1 убран, чтобы не светился на форме
    MatchForm = modelform_factory(
        Match,
        fields=["player2", "date", "time", "location", "status", "score"],
    )


@login_required
def match_list(request):
    qs = Match.objects.all().select_related(
        *[f.name for f in Match._meta.fields if f.is_relation and f.many_to_one]
    ).order_by("-date", "-time")

    q = request.GET.get("q")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if q:
        qs = qs.filter(
            Q(location__icontains=q)
            | Q(player1__first_name__icontains=q) | Q(player1__last_name__icontains=q)
            | Q(player2__first_name__icontains=q) | Q(player2__last_name__icontains=q)
        )
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    return render(request, "matches/match_list.html", {
        "matches": qs,
        "filters_open": request.GET.get("filters", "false"),
    })


@login_required
def match_add(request):
    if request.method == "POST":
        form = MatchForm(request.POST)
        if form.is_valid():
            match = form.save(commit=False)
            # Автоматически ставим текущего игрока как player1
            match.player1 = request.user.player_profile
            if not match.player2:
                match.status = "open"
            match.save()
            messages.success(request, "Матч создан.")
            return redirect("match_detail", pk=match.pk)
    else:
        form = MatchForm()
    return render(request, "matches/match_form.html", {"form": form})


@login_required
def match_detail(request, pk):
    match = get_object_or_404(Match, pk=pk)
    return render(request, "matches/match_detail.html", {"match": match})


@login_required
def match_edit(request, pk):
    match = get_object_or_404(Match, pk=pk)
    if request.method == "POST":
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            messages.success(request, "Матч обновлён.")
            return redirect("match_detail", pk=match.pk)
    else:
        form = MatchForm(instance=match)
    return render(request, "matches/match_form.html", {"form": form, "match": match})


@login_required
def match_delete(request, pk):
    match = get_object_or_404(Match, pk=pk)
    if request.method == "POST":
        match.delete()
        messages.success(request, "Матч удалён.")
        return redirect("match_list")
    return render(request, "matches/match_confirm_delete.html", {"object": match})


@login_required
def join_match(request, pk):
    """Присоединиться ко второму слоту матча."""
    match = get_object_or_404(Match, pk=pk)

    if match.player2 is not None or match.status != "open":
        messages.error(request, "Нельзя присоединиться — матч уже занят или закрыт.")
        return redirect("match_detail", pk=pk)

    if match.player1 == request.user.player_profile:
        messages.error(request, "Вы не можете присоединиться к своему же матчу.")
        return redirect("match_detail", pk=pk)

    match.player2 = request.user.player_profile
    match.status = "scheduled"
    match.save()

    messages.success(request, "Вы успешно присоединились к матчу!")
    return redirect("match_detail", pk=pk)


@login_required
def leave_match(request, pk):
    """Позволяет player2 выйти из матча."""
    match = get_object_or_404(Match, pk=pk)

    me = request.user.player_profile
    if match.player2 != me:
        messages.error(request, "Вы не можете выйти из этого матча.")
        return redirect("match_detail", pk=pk)

    if request.method == "POST":
        match.player2 = None
        match.status = "open"   # снова открыт для поиска соперника
        match.save()
        messages.success(request, "Вы вышли из матча.")
        return redirect("match_detail", pk=pk)

    return render(request, "matches/match_confirm_leave.html", {"match": match})
