# tennis_site/settings.py
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
# Управлять DEBUG через env: в продакшне установи DEBUG=False
DEBUG = os.getenv("DEBUG", "True").lower() in ("1", "true", "yes")

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
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

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
    # Важно: наш middleware должен стоять как можно раньше,
    # чтобы быстро отбрасывать множественные регистрации
    "tennis_site.middleware.registration_rate_limit.RegistrationRateLimitMiddleware",

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

# === Кэш (Redis если задан REDIS_URL, иначе локальный) ===
# Для продакшна рекомендую указать REDIS_URL в .env: REDIS_URL=redis://:password@host:6379/1
REDIS_URL = os.getenv("REDIS_URL", "").strip()

if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
else:
    # ВНИМАНИЕ: LocMemCache не подходит для нескольких процессов/инстансов,
    # но работает локально/на этапе разработки.
    CACHES = {
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
    }

# === Cloudinary (как в твоём файле) ===
# Если ты используешь CLOUDINARY_URL в .env, можно раскомментировать
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL", "")

USE_CLOUDINARY = bool(CLOUDINARY_URL and CLOUDINARY_URL.startswith("cloudinary://"))

if USE_CLOUDINARY:
    try:
        cloudinary.config(cloudinary_url=CLOUDINARY_URL, secure=True)
        cloudinary.api.ping()
        DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
        print("✅ Cloudinary: используем облачное хранилище.")
    except Exception as e:
        print(f"⚠️ Cloudinary недоступен ({e}), используем локальное хранилище.")
        DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
else:
    print("⚠️ Cloudinary не настроен. Используется локальное хранилище.")
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# === Медиа ===
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# === Статические файлы ===
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

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

# --- Регистрационный rate-limit (нашныe настройки для middleware) ---
# Максимум регистраций с одного IP в окне
REG_RATE_LIMIT = int(os.getenv("REG_RATE_LIMIT", "5"))          # например 5 попыток
REG_RATE_WINDOW = int(os.getenv("REG_RATE_WINDOW", "3600"))    # окно в секундах (1 час)
# Пути, которые будем отслеживать (поставь реальные пути регистрации в твоём проекте)
REG_RATE_CHECK_PATHS = [
    "/accounts/register/",
    "/api/register/",
    "/users/register/",
]
REG_BLOCK_STATUS = int(os.getenv("REG_BLOCK_STATUS", "429"))
# Какой заголовок брать для IP, если ты стоишь за proxy / CDN (X-Forwarded-For)
REG_TRUSTED_PROXY_HEADER = os.getenv("REG_TRUSTED_PROXY_HEADER", "HTTP_X_FORWARDED_FOR")
REG_RATE_CACHE_ALIAS = os.getenv("REG_RATE_CACHE_ALIAS", "default")
# Белый список IP (например для локального теста/CI)
REG_RATE_WHITELIST = os.getenv("REG_RATE_WHITELIST", "127.0.0.1,::1").split(",")

# === Прочее (оставлено как в твоём файле) ===
UNIVERSAL_API_KEY = os.getenv("UNIVERSAL_API_KEY", "super-secret-key-123")

