from decimal import Decimal, InvalidOperation
from django import forms
from .models import Tournament

# Можно править под свои градации
LEVEL_CHOICES = [
    ("1.0", "1.0"),
    ("1.5", "1.5"),
    ("2.0", "2.0"),
    ("2.5", "2.5"),
    ("3.0", "3.0"),
    ("3.5", "3.5"),
    ("4.0", "4.0"),
    ("4.5", "4.5"),
    ("5.0", "5.0"),
    ("5.5", "5.5"),
    ("6.0", "6.0"),
    ("7.0", "7.0"),
]

FORMAT_CHOICES = [
    (16, "16 (плей-офф)"),
    (32, "32 (плей-офф)"),
    (64, "64 (группы → плей-офф)"),
]


class TournamentForm(forms.ModelForm):
    """
    ВАЖНО:
    - min_level / max_level приходят как строки из select'а. В clean()
      переводим "" → None, "5.5" → Decimal("5.5") перед сохранением.
    - max_players здесь не используем: вместимость = format.
    """
    # Поля уровня — необязательные селекты
    min_level = forms.ChoiceField(
        choices=[("", "Без ограничения")] + LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    max_level = forms.ChoiceField(
        choices=[("", "Без ограничения")] + LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    # Формат турнира — фиксированные значения
    format = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    # Остальные поля — обычные
    name = forms.CharField(
        label="Название",
        widget=forms.TextInput(attrs={"class": "form-control", "maxlength": 120, "placeholder": "Например: ALMATY OPEN"})
    )
    location = forms.CharField(
        label="Локация",
        widget=forms.TextInput(attrs={"class": "form-control", "maxlength": 120, "placeholder": "Город, корт"})
    )
    date = forms.DateField(
        label="Дата",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    time = forms.TimeField(
        label="Время",
        required=False,
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"})
    )
    description = forms.CharField(
        label="Описание",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Доп. информация"})
    )

    class Meta:
        model = Tournament
        # ВМЕСТО max_players используем format
        fields = ["name", "location", "date", "time", "format", "min_level", "max_level", "description"]

    # ---- вспомогательное
    @staticmethod
    def _to_dec_or_none(value: str | None):
        if not value:
            return None
        try:
            return Decimal(value)
        except (InvalidOperation, ValueError):
            # отдадим валидационную ошибку выше
            raise forms.ValidationError("Уровень должен быть числом вида 5.0 / 5.5 / 6.0 и т.д.")

    def clean(self):
        cleaned = super().clean()

        # формат (ChoiceField) приходит строкой → приведём к int
        fmt_raw = cleaned.get("format")
        if fmt_raw in (None, ""):
            raise forms.ValidationError("Выберите формат турнира (16 / 32 / 64).")
        try:
            cleaned["format"] = int(fmt_raw)
        except ValueError:
            raise forms.ValidationError("Неверный формат значения поля 'format'.")

        # уровни — из select: "" → None, "5.5" → Decimal("5.5")
        min_raw = cleaned.get("min_level")
        max_raw = cleaned.get("max_level")

        min_dec = self._to_dec_or_none(min_raw)
        max_dec = self._to_dec_or_none(max_raw)

        if min_dec is not None and max_dec is not None and min_dec > max_dec:
            raise forms.ValidationError("Минимальный уровень не может быть больше максимального.")

        cleaned["min_level"] = min_dec
        cleaned["max_level"] = max_dec
        return cleaned
