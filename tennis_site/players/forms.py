from django import forms
from .models import Player, Achievement


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ["first_name", "last_name", "age", "level", "photo", "phone_number", "address"]
        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-control text-center",
                "placeholder": "Введите имя",
                "maxlength": 30
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control text-center",
                "placeholder": "Введите фамилию",
                "maxlength": 30
            }),
            "age": forms.NumberInput(attrs={
                "class": "form-control text-center",
                "min": 5, "max": 120,
                "placeholder": "Возраст"
            }),
            "level": forms.Select(attrs={
                "class": "form-select text-center"
            }),
            "photo": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
            "phone_number": forms.TextInput(attrs={
                "class": "form-control text-center",
                "placeholder": "Введите номер телефона",
                "maxlength": 15,
                "pattern": r"\d+"  # только цифры
            }),
            "address": forms.TextInput(attrs={
                "class": "form-control text-center",
                "placeholder": "Адрес проживания",
                "maxlength": 100
            }),
        }


class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ["title", "description", "photo"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control text-center",
                "placeholder": "Введите название достижения",
                "maxlength": 50
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control text-center",
                "placeholder": "Опишите достижение",
                "rows": 4,
                "maxlength": 300
            }),
            "photo": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
        }


class PlayerProfileForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ["first_name", "last_name", "age", "level", "photo", "phone_number", "address"]
        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-control text-center",
                "placeholder": "Введите имя",
                "maxlength": 30
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control text-center",
                "placeholder": "Введите фамилию",
                "maxlength": 30
            }),
            "age": forms.NumberInput(attrs={
                "class": "form-control text-center",
                "min": 5, "max": 120,
                "placeholder": "Возраст"
            }),
            "level": forms.Select(attrs={
                "class": "form-select text-center"
            }),
            "photo": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
            "phone_number": forms.TextInput(attrs={
                "class": "form-control text-center",
                "placeholder": "Введите номер телефона",
                "maxlength": 15,
                "pattern": r"\d+"  # только цифры
            }),
            "address": forms.TextInput(attrs={
                "class": "form-control text-center",
                "placeholder": "Адрес проживания",
                "maxlength": 100
            }),
        }


class PlayerFilterForm(forms.Form):
    name = forms.CharField(
        label="ФИО", required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Имя или фамилия",
            "maxlength": 50
        })
    )
    min_age = forms.IntegerField(
        label="Возраст от", required=False,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "от",
            "min": 5, "max": 120
        })
    )
    max_age = forms.IntegerField(
        label="до", required=False,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "до",
            "min": 5, "max": 120
        })
    )
    level = forms.ChoiceField(
        label="Уровень игры", required=False,
        choices=[("", "Любой")] + list(Player._meta.get_field("level").choices),
        widget=forms.Select(attrs={"class": "form-select"})
    )
    address = forms.CharField(
        label="Город", required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Например: Алматы",
            "maxlength": 100
        })
    )
