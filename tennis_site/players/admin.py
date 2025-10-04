from django.contrib import admin
from .models import Player, Achievement

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "age", "level")
    search_fields = ("first_name", "last_name")
    list_filter = ("level",)
    ordering = ("last_name", "first_name")
    list_per_page = 25

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("title", "player", "date")
    search_fields = ("title", "player__first_name", "player__last_name")
    list_filter = ("date",)
    ordering = ("-date",)
    list_per_page = 20
