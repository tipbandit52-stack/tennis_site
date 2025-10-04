from django.contrib import admin
from .models import Tournament, Group, GroupMatch, BracketMatch

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "date", "time", "format", "status", "creator")
    list_filter = ("format", "status", "date", "location")
    search_fields = ("name", "location")
    ordering = ("-date",)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("tournament", "code")
    list_filter = ("tournament",)

@admin.register(GroupMatch)
class GroupMatchAdmin(admin.ModelAdmin):
    list_display = ("group", "p1", "p2", "p1_score", "p2_score", "winner")
    list_filter = ("group__tournament", "group__code")

@admin.register(BracketMatch)
class BracketMatchAdmin(admin.ModelAdmin):
    list_display = ("tournament", "round_no", "slot", "p1", "p2", "p1_score", "p2_score", "winner")
    list_filter = ("tournament", "round_no")
    ordering = ("tournament", "round_no", "slot")
