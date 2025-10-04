from django import forms
from .models import Match


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ["player2", "date", "time", "location"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control", "placeholder": "Место проведения"}),
            "player2": forms.Select(attrs={"class": "form-select"}),
        }
