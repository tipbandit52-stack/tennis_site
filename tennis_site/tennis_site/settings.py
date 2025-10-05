from pathlib import Path
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api

# === Загрузка .env ===
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# === Безопасность ===
SECRET_KEY = os.getenv("SECRET_KEY", "замени-на-секретный-ключ")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# === Разрешённые хосты ===
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "tennis-site.onrender.com",
    "litetennis.kz",
    "www.litetennis.kz",
]

# === CSRF и Cookies ===
CSRF_TRUSTED_ORIGINS = [
    "https://tennis-site.onrender.com",
    "https://litetennis.kz",
    "https://www.litetennis.kz",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

SESSION_COOKIE_SAMESITE = None
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# === Приложения ===
INSTALLED_APPS = [
    # внешние
    "cloudinary",
    "cloudinary_storage",
    "widget_tweaks",
    "channels",

    # твои приложения
    "api",
    "tournaments",
    "friends",
    "chat",
    "matches",
    "users",
    "players",

    # стандартные Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# === Middleware ===
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "tennis_site.urls"

# === Templates ===
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# === ASGI и Channels ===
ASGI_APPLICATION = "tennis_site.asgi.application"
CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
}

# === База данных (SQLite — локально) ===
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# === Cloudinary ===
from django.core.exceptions import ImproperlyConfigured

CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")

if CLOUDINARY_URL and CLOUDINARY_URL.startswith("cloudinary://"):
    try:
        # Основная настройка
        cloudinary.config(cloudinary_url=CLOUDINARY_URL, secure=True)
        print("✅ Cloudinary подключён:", cloudinary.config().cloud_name)

        # Проверим соединение (ping)
        try:
            cloudinary.api.ping()
            print("✅ Cloudinary доступен, используется облачное хранилище.")
            DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
        except Exception as ping_err:
            print(f"⚠️ Cloudinary не отвечает ({ping_err}), переключаюсь на локальное хранилище.")
            DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

    except ImproperlyConfigured as config_err:
        print(f"⚠️ Ошибка конфигурации Cloudinary: {config_err}")
        DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

else:
    print("⚠️ Переменная CLOUDINARY_URL не найдена или некорректна. Используется локальное хранилище.")
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"


# === Статические файлы ===
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# === Медиа ===
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# === Проверка — если Cloudinary падает, фото не ломаются ===
try:
    cloudinary.api.ping()
except Exception as e:
    print("⚠️ Cloudinary недоступен, фото сохранятся локально.")
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# === Авторизация ===
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "my_profile"
LOGOUT_REDIRECT_URL = "index"

# === Локализация ===
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Asia/Almaty"
USE_I18N = True
USE_TZ = True

# === Прочие настройки ===
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
UNIVERSAL_API_KEY = os.getenv("UNIVERSAL_API_KEY", "super-secret-key-123")
