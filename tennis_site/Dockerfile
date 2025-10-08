# ==== БАЗОВЫЙ ОБРАЗ ====
FROM python:3.13-slim

# ==== СИСТЕМНЫЕ НАСТРОЙКИ ====
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# ==== РАБОЧАЯ ДИРЕКТОРИЯ ====
WORKDIR /app

# ==== ЗАВИСИМОСТИ ====
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==== КОПИРУЕМ ПРОЕКТ ====
COPY . .

# ==== СТАТИЧЕСКИЕ ФАЙЛЫ ====
RUN python manage.py collectstatic --noinput || true

# ==== КОМАНДА ЗАПУСКА ====
CMD ["gunicorn", "tennis_site.wsgi:application", "--bind", "0.0.0.0:8080"]
